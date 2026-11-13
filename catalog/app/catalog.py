"""In-memory search index over the Microsoft Learn catalog file (ms-learn-api.json).

Every record in the file is kept unchanged and returned as-is, so callers get all of its fields.
The index supports keyword search (title, summary, tags), optional filters by roles, levels, products
and type, and ranking by popularity. Nothing here touches the network.
"""
from __future__ import annotations

import bisect
import datetime as dt
import html
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

STOP_WORDS = frozenset({
    "a", "an", "and", "the", "of", "to", "for", "in", "on", "with", "how", "use", "using",
    "microsoft", "or", "is", "are", "at", "by", "from", "your",
})

# Collection name in the catalog file -> public type name used by the API.
COLLECTION_TYPES = {
    "modules": "module",
    "units": "unit",
    "learningPaths": "learningPath",
    "appliedSkills": "appliedSkill",
    "certifications": "certification",
    "mergedCertifications": "certification",
    "exams": "exam",
    "courses": "course",
}
TAXONOMIES = ("levels", "products", "roles", "subjects")
# Units (27k+ one-line lessons without roles, levels or popularity) are searchable only on request.
DEFAULT_TYPES = frozenset(t for t in COLLECTION_TYPES.values() if t != "unit")
# Fields whose values are uids (or {"uid": ...} objects) of other records.
REFERENCE_FIELDS = ("modules", "units", "exams", "courses", "study_guide", "certification", "exam")

_WORD = re.compile(r"[a-z0-9]+")
_TAG = re.compile(r"<[^>]+>")
# A class code is 1-4 letters, 2-4 digits, and an optional delivery suffix such as T00 (AB-650T00, AI-3025).
_CODE = re.compile(r"^(?P<prefix>[A-Z]{1,4})(?P<number>\d{2,4})(?P<suffix>[A-Z]\d{2})?$")


def parse_class_code(text: Any) -> tuple[str, str] | None:
    """Return (key, suffix) for a class code, or None when the text is not one.

    The key is the code without punctuation, case or the delivery suffix, so "AI-3025", "ai3025" and
    "AI-3025T00" all give the key "AI3025".
    """
    if not isinstance(text, str):
        return None
    match = _CODE.match(re.sub(r"[^A-Z0-9]", "", text.upper()))
    return (match["prefix"] + match["number"], match["suffix"] or "") if match else None


def _norm(token: str) -> str:
    """Fold simple plurals so "agents" matches "agent"."""
    if len(token) > 3 and token.endswith("s") and not token.endswith("ss"):
        return token[:-1]
    return token


def tokenize(text: Any) -> list[str]:
    if not isinstance(text, str) or not text:
        return []
    text = html.unescape(_TAG.sub(" ", text)).lower()
    return [_norm(w) for w in _WORD.findall(text) if len(w) >= 2 and w not in STOP_WORDS]


@dataclass(slots=True)
class Entry:
    uid: str
    type: str
    collections: list[str]
    item: dict[str, Any]
    title: str
    popularity: float | None
    link: str
    roles: frozenset[str]
    levels: frozenset[str]
    products: frozenset[str]
    title_tokens: frozenset[str]
    tag_tokens: frozenset[str]
    text_tokens: frozenset[str]
    class_key: str | None = None

def _taxonomy_names(nodes: list[dict[str, Any]], out: dict[str, str]) -> None:
    for node in nodes:
        out[node["id"]] = node.get("name", "")
        _taxonomy_names(node.get("children", []), out)


def _merge_records(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    """Merge two records with the same uid. Lists that differ are unioned, so nothing is lost."""
    merged = {**a, **b}
    for key in set(a) & set(b):
        if a[key] != b[key] and isinstance(a[key], list) and isinstance(b[key], list):
            seen, union = set(), []
            for value in a[key] + b[key]:
                marker = json.dumps(value, sort_keys=True)
                if marker not in seen:
                    seen.add(marker)
                    union.append(value)
            merged[key] = union
    return merged


class Catalog:
    def __init__(self, raw: dict[str, Any], source: str = "", file_modified: str = "") -> None:
        self.source = source
        self.file_modified = file_modified
        self.loaded_at = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
        self.taxonomies = {name: raw.get(name, []) for name in TAXONOMIES}
        self.raw_counts = {name: len(raw.get(name, [])) for name in COLLECTION_TYPES}

        names: dict[str, dict[str, str]] = {}
        for tax in TAXONOMIES:
            names[tax] = {}
            _taxonomy_names(self.taxonomies[tax], names[tax])
        self.taxonomy_ids = {tax: set(n) for tax, n in names.items()}

        records: dict[str, dict[str, Any]] = {}
        types: dict[str, str] = {}
        collections: dict[str, list[str]] = {}
        self.skipped: list[dict[str, str]] = []
        for coll, public_type in COLLECTION_TYPES.items():
            for rec in raw.get(coll, []):
                uid = rec.get("uid")
                if not uid:
                    continue
                if uid not in records:
                    records[uid], types[uid], collections[uid] = rec, public_type, [coll]
                elif types[uid] == public_type:
                    records[uid] = _merge_records(records[uid], rec)
                    collections[uid].append(coll)
                else:
                    self.skipped.append({"uid": uid, "collection": coll, "reason": "uid used by another type"})

        self.entries: list[Entry] = []
        self.by_uid: dict[str, int] = {}
        for uid, rec in records.items():
            self.by_uid[uid] = len(self.entries)
            self.entries.append(self._entry(uid, types[uid], collections[uid], rec, names))

        self.index: dict[str, list[int]] = {}
        for idx, e in enumerate(self.entries):
            for token in e.title_tokens | e.tag_tokens | e.text_tokens:
                self.index.setdefault(token, []).append(idx)
        self.vocab = sorted(self.index)

        self.referenced_by: dict[str, list[int]] = {}
        for idx, e in enumerate(self.entries):
            for target in self._references(e.item):
                if target in self.by_uid:
                    self.referenced_by.setdefault(target, []).append(idx)

        # Classes are the instructor-led courses. Those with a real class code can be looked up by it.
        self.class_index: dict[str, list[int]] = {}
        self.class_numbers: dict[str, list[tuple[int, str]]] = {}   # letters -> [(number, key)]
        self.classes_total = 0
        for idx, e in enumerate(self.entries):
            if e.type != "course":
                continue
            self.classes_total += 1
            if e.class_key:
                self.class_index.setdefault(e.class_key, []).append(idx)
        for key in self.class_index:
            prefix, number = re.match(r"([A-Z]+)(\d+)", key).groups()
            self.class_numbers.setdefault(prefix, []).append((int(number), key))

    @classmethod
    def load(cls, path: str | Path) -> "Catalog":
        path = Path(path)
        with path.open(encoding="utf-8") as fh:
            raw = json.load(fh)
        modified = dt.datetime.fromtimestamp(path.stat().st_mtime, dt.timezone.utc).isoformat(timespec="seconds")
        return cls(raw, source=str(path), file_modified=modified)

    # ------------------------------------------------------------------ building

    @staticmethod
    def _entry(uid, public_type, colls, rec, names) -> Entry:
        popularity = rec.get("popularity")
        popularity = float(popularity) if isinstance(popularity, (int, float)) else None
        title = str(rec.get("title") or rec.get("display_name") or "")
        url = str(rec.get("url") or "")

        title_tokens = set(tokenize(title)) | set(tokenize(rec.get("display_name")))
        title_tokens |= set(tokenize(rec.get("course_number")))
        tag_tokens: set[str] = set()
        for tax in TAXONOMIES:
            for ident in rec.get(tax, []) or []:
                tag_tokens.update(tokenize(ident))
                tag_tokens.update(tokenize(names[tax].get(ident, "")))
        text_tokens = set(tokenize(rec.get("summary"))) | set(tokenize(rec.get("subtitle")))
        for skill in rec.get("skills", []) or []:
            text_tokens.update(tokenize(skill))

        parsed = parse_class_code(rec.get("course_number")) if public_type == "course" else None
        return Entry(
            uid=uid, type=public_type, collections=colls, item=rec, title=title, popularity=popularity,
            link=url.split("?")[0], roles=frozenset(rec.get("roles", []) or []),
            levels=frozenset(rec.get("levels", []) or []), products=frozenset(rec.get("products", []) or []),
            title_tokens=frozenset(title_tokens), tag_tokens=frozenset(tag_tokens - title_tokens),
            text_tokens=frozenset(text_tokens - title_tokens - tag_tokens),
            class_key=parsed[0] if parsed else None,
        )

    @staticmethod
    def _references(item: dict[str, Any]):
        for key in REFERENCE_FIELDS:
            value = item.get(key)
            if not value:
                continue
            for ref in value if isinstance(value, list) else [value]:
                uid = ref.get("uid") if isinstance(ref, dict) else ref
                if isinstance(uid, str):
                    yield uid

    # ------------------------------------------------------------------ search

    def _expand(self, token: str) -> set[str]:
        """The token itself plus indexed words that start with it (prefix match from 3 letters)."""
        found = {token} if token in self.index else set()
        if len(token) >= 3:
            pos = bisect.bisect_left(self.vocab, token)
            while pos < len(self.vocab) and self.vocab[pos].startswith(token):
                found.add(self.vocab[pos])
                pos += 1
        return found

    def _postings(self, words: set[str]) -> set[int]:
        out: set[int] = set()
        for word in words:
            out.update(self.index[word])
        return out

    @staticmethod
    def _score(e: Entry, expansions: dict[str, set[str]]) -> tuple[float, list[str]]:
        score, matched = 0.0, []
        for token, words in expansions.items():
            if not e.title_tokens.isdisjoint(words):
                weight = 3.0
            elif not e.tag_tokens.isdisjoint(words):
                weight = 1.5
            elif not e.text_tokens.isdisjoint(words):
                weight = 1.0
            else:
                continue
            score += weight
            matched.append(token)
        return score, matched

    def warnings_for(self, roles, levels, products) -> list[str]:
        out = []
        for label, values, tax in (("roles", roles, "roles"), ("levels", levels, "levels"), ("products", products, "products")):
            unknown = sorted(v for v in values if v not in self.taxonomy_ids[tax])
            if unknown:
                out.append(f"Unknown {label}: {', '.join(unknown)}. See /taxonomies/{tax} for valid ids.")
        return out

    def _rows(self, q, *, roles=(), levels=(), products=(), types=(), match="all", sort="popularity"):
        """All matching records as (entry, score, matched terms), best first, before paging."""
        tokens = list(dict.fromkeys(tokenize(q)))
        expansions = {t: self._expand(t) for t in tokens}

        if tokens:
            sets = sorted((self._postings(words) for words in expansions.values()), key=len)
            candidates = set.intersection(*sets) if match == "all" else set.union(*sets)
        else:
            candidates = range(len(self.entries))

        type_set = set(types) or DEFAULT_TYPES
        role_set, level_set, product_set = set(roles), set(levels), set(products)
        rows = []
        for idx in candidates:
            e = self.entries[idx]
            if e.type not in type_set:
                continue
            if role_set and e.roles.isdisjoint(role_set):
                continue
            if level_set and e.levels.isdisjoint(level_set):
                continue
            if product_set and e.products.isdisjoint(product_set):
                continue
            score, matched = self._score(e, expansions) if tokens else (0.0, [])
            rows.append((e, score, matched))

        def popularity_key(row):
            e, score, _ = row
            return (e.popularity is None, -(e.popularity or 0.0), -score, e.title.lower())

        def relevance_key(row):
            e, score, _ = row
            return (-score, e.popularity is None, -(e.popularity or 0.0), e.title.lower())

        rows.sort(key=relevance_key if sort == "relevance" else popularity_key)
        return tokens, rows

    def search(self, q: str | None = None, *, roles=(), levels=(), products=(), types=(),
               match: str = "all", sort: str = "popularity", limit: int = 10, offset: int = 0):
        tokens, rows = self._rows(q, roles=roles, levels=levels, products=products, types=types, match=match, sort=sort)
        page = rows[offset: offset + limit]
        results = [self.wrap(e, score=score, matched=matched) for e, score, matched in page]
        return tokens, len(rows), results

    # ------------------------------------------------------------------ classes

    def find_class(self, code: str) -> tuple[Entry | None, list[Entry]]:
        """Look a class up by its code (case, punctuation and the T00 suffix do not matter).

        Returns (class, other classes with the same code). The class is None when there is no match.
        """
        parsed = parse_class_code(code)
        if not parsed:
            return None, []
        key, suffix = parsed
        matches = [self.entries[i] for i in self.class_index.get(key, [])]
        if not matches:
            return None, []
        matches.sort(key=lambda e: str(e.item.get("course_number")))
        if suffix:   # the caller named a delivery suffix: prefer the class that has it
            exact = [e for e in matches if (parse_class_code(e.item.get("course_number")) or ("", ""))[1] == suffix]
            if exact:
                matches = exact + [e for e in matches if e not in exact]
        return matches[0], matches[1:]

    def suggest_classes(self, code: str, limit: int = 5) -> list[dict[str, str]]:
        """Classes that are close to a code that was not found."""
        parsed = parse_class_code(code)
        if not parsed:
            return []
        key = parsed[0]
        prefix, number = re.match(r"([A-Z]+)(\d+)", key).groups()
        wanted = int(number)
        ranked: list[tuple[tuple[int, int], str, str]] = []
        for num, other in self.class_numbers.get(prefix, []):
            ranked.append(((0, abs(num - wanted)), other, "same prefix, nearest number"))
        for other_prefix, items in self.class_numbers.items():
            if other_prefix != prefix:
                ranked.extend(((1, 0), other, "same number, different prefix") for num, other in items if num == wanted)
        ranked.sort(key=lambda row: (row[0], row[1]))
        suggestions = []
        for _, other, reason in ranked[:limit]:
            e = self.entries[self.class_index[other][0]]
            suggestions.append({"uid": e.uid, "code": str(e.item.get("course_number")), "title": e.title,
                                "link": e.link, "reason": reason})
        return suggestions

    def find_classes(self, q: str | None = None, *, roles=(), levels=(), products=(), match: str = "all",
                     limit: int = 5, offset: int = 0):
        """Search classes by code or by words in their name. A class whose code equals the query comes first."""
        role_set, level_set, product_set = set(roles), set(levels), set(products)

        def allowed(e: Entry) -> bool:
            return not ((role_set and e.roles.isdisjoint(role_set)) or (level_set and e.levels.isdisjoint(level_set))
                        or (product_set and e.products.isdisjoint(product_set)))

        rows: list[tuple[Entry, float | None, list[str], str]] = []
        seen: set[str] = set()
        code_query = parse_class_code(q) if q else None
        if code_query:
            exact, others = self.find_class(q)
            for e in ([exact] + others) if exact else []:
                if allowed(e):
                    rows.append((e, None, [], "code"))
                    seen.add(e.uid)
        tokens, keyword_rows = self._rows(q, roles=roles, levels=levels, products=products, types=("course",),
                                          match=match, sort="relevance")
        rows += [(e, score, matched, "keywords") for e, score, matched in keyword_rows if e.uid not in seen]
        page = rows[offset: offset + limit]
        suggestions = self.suggest_classes(q) if code_query and not any(r[3] == "code" for r in rows) else []
        return tokens, code_query[0] if code_query else None, len(rows), page, suggestions

    def class_contents(self, e: Entry) -> dict[str, Any]:
        """The learning paths and modules a class covers, from its study guide.

        A study guide lists learning paths (each with an ordered list of modules) and sometimes modules directly.
        Modules are returned once each, in study-guide order, with the paths they came through.
        """
        paths: dict[str, dict[str, Any]] = {}
        modules: dict[str, dict[str, Any]] = {}
        unresolved: list[dict[str, str]] = []

        def add_module(module: Entry, via: str | None) -> None:
            if module.uid not in modules:
                modules[module.uid] = {**self.wrap(module), "via_learning_paths": [], "direct": False}
            if via:
                if via not in modules[module.uid]["via_learning_paths"]:
                    modules[module.uid]["via_learning_paths"].append(via)
            else:
                modules[module.uid]["direct"] = True

        for ref in e.item.get("study_guide", []) or []:
            uid = ref.get("uid") if isinstance(ref, dict) else ref
            target = self.get(uid) if isinstance(uid, str) else None
            if target is None:
                unresolved.append({"field": "study_guide", "uid": str(uid), "in": e.uid, "reason": "not in the catalog"})
            elif target.type == "learningPath":
                if target.uid in paths:
                    continue
                paths[target.uid] = self.wrap(target)
                for module_uid in target.item.get("modules", []) or []:
                    module = self.get(module_uid)
                    if module is None or module.type != "module":
                        unresolved.append({"field": "modules", "uid": str(module_uid), "in": target.uid, "reason": "not in the catalog"})
                    else:
                        add_module(module, target.uid)
            elif target.type == "module":
                add_module(target, None)
            else:
                unresolved.append({"field": "study_guide", "uid": target.uid, "in": e.uid,
                                   "reason": f"a {target.type} is not a learning path or module"})

        minutes = sum(int(m["item"].get("duration_in_minutes") or 0) for m in modules.values())
        return {
            "learning_paths": list(paths.values()),
            "modules": list(modules.values()),
            "unresolved": unresolved,
            "totals": {"learning_paths": len(paths), "modules": len(modules), "duration_minutes": minutes,
                       "unresolved": len(unresolved)},
        }

    # ------------------------------------------------------------------ records

    @staticmethod
    def wrap(e: Entry, score: float | None = None, matched: list[str] | None = None) -> dict[str, Any]:
        out = {"uid": e.uid, "type": e.type, "collections": e.collections, "link": e.link,
               "popularity": e.popularity, "item": e.item}
        if score is not None:
            out["score"] = round(score, 2)
            out["matched_terms"] = matched or []
        return out

    def get(self, uid: str) -> Entry | None:
        idx = self.by_uid.get(uid)
        return self.entries[idx] if idx is not None else None

    def expand(self, e: Entry) -> dict[str, Any]:
        """Resolve the uids a record points to, and list the records that point to it."""
        resolved: dict[str, list[dict[str, Any]]] = {}
        unresolved: list[dict[str, str]] = []
        for key in REFERENCE_FIELDS:
            value = e.item.get(key)
            if not value:
                continue
            found = []
            for ref in value if isinstance(value, list) else [value]:
                uid = ref.get("uid") if isinstance(ref, dict) else ref
                if not isinstance(uid, str):
                    continue
                target = self.get(uid)
                if target:
                    found.append(self.wrap(target))
                else:
                    unresolved.append({"field": key, "uid": uid})
            if found:
                resolved[key] = found
        referenced_by = [
            {"uid": o.uid, "type": o.type, "title": o.title, "link": o.link}
            for o in (self.entries[i] for i in self.referenced_by.get(e.uid, []))
        ]
        return {"resolved": resolved, "unresolved": unresolved, "referenced_by": referenced_by}

    def meta(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "file_modified": self.file_modified,
            "loaded_at": self.loaded_at,
            "records": len(self.entries),
            "searchable_by_default": sum(1 for e in self.entries if e.type in DEFAULT_TYPES),
            "collections": self.raw_counts,
            "taxonomies": {k: len(v) for k, v in self.taxonomies.items()},
            "merged_duplicate_uids": sum(1 for e in self.entries if len(e.collections) > 1),
            "classes": {"total": self.classes_total, "with_code": sum(len(v) for v in self.class_index.values()),
                        "without_code": self.classes_total - sum(len(v) for v in self.class_index.values())},
            "skipped_records": self.skipped,
        }
