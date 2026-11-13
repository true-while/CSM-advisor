import copy
import json
from pathlib import Path

import pytest

from app.catalog import parse_class_code
from test_api import FIXTURE, make_client

REAL_FILE = Path(__file__).resolve().parent.parent / "ms-learn-api.json"


def module(uid, title, minutes, **extra):
    return {"uid": uid, "type": "module", "title": title, "summary": "A module.", "levels": ["beginner"],
            "roles": ["business-user"], "products": ["microsoft-365-copilot"], "duration_in_minutes": minutes,
            "popularity": 0.5, "url": f"https://learn.microsoft.com/en-us/training/modules/{uid}/?WT.mc_id=api",
            "units": [], **extra}


def path(uid, title, modules):
    return {"uid": uid, "type": "learningPath", "title": title, "summary": "A path.", "levels": ["beginner"],
            "roles": ["business-user"], "products": ["microsoft-365-copilot"], "duration_in_minutes": 100,
            "popularity": 0.5, "url": f"https://learn.microsoft.com/en-us/training/paths/{uid}/?WT.mc_id=api",
            "modules": modules}


def course(uid, number, title, guide, **extra):
    return {"uid": uid, "type": "course", "course_number": number, "title": title, "summary": "<p>A class.</p>",
            "levels": ["beginner"], "roles": ["business-user"], "products": ["microsoft-365-copilot"],
            "duration_in_hours": 8, "url": f"https://learn.microsoft.com/en-us/training/courses/{uid}/?WT.mc_id=api",
            "study_guide": [{"uid": u, "type": t} for u, t in guide], "recommendation_list": [], **extra}


@pytest.fixture()
def data():
    d = copy.deepcopy(FIXTURE)
    d["modules"] += [
        module("m.one", "Robots part one", 10), module("m.two", "Robots part two", 20),
        module("m.three", "Robots part three", 30), module("m.direct", "Directly listed module", 5),
        module("m.admin", "Identity for administrators", 7, roles=["administrator"], levels=["intermediate"]),
    ]
    d["learningPaths"] += [
        path("p.a", "Robots basics", ["m.one", "m.two", "m.missing"]),
        path("p.b", "Robots advanced", ["m.two", "m.three"]),
    ]
    d["courses"] += [
        course("course.ai3025", "AI-3025", "Work smarter with robots", [("p.a", "learningPath")]),
        course("course.sc300", "SC-300T00", "Identity and access", [
            ("m.direct", "module"), ("p.a", "learningPath"), ("p.b", "learningPath"), ("p.gone", "learningPath"),
            ("exam.y", "exam"), ("p.a", "learningPath")], roles=["administrator"], levels=["intermediate"]),
        course("course.nocode", "", "Classroom stories", [("p.b", "learningPath")]),
        course("course.alias", "MSLEFooBootcamp", "Bootcamp thing", []),
        course("course.xy100a", "XY-100T00", "Same code, first delivery", [("m.direct", "module")]),
        course("course.xy100b", "XY-100T01", "Same code, second delivery", [("m.one", "module")]),
        course("course.decoy", "ZZ-999", "AI 3025 revision notes", []),   # its NAME mentions AI 3025; its code does not match
    ]
    return d


@pytest.fixture()
def client(tmp_path, monkeypatch, data):
    with make_client(tmp_path, monkeypatch, data) as c:
        yield c


def ids(items):
    return [i["uid"] for i in items]


@pytest.mark.parametrize("text,expected", [
    ("AI-3015", ("AI3015", "")), ("ai3015", ("AI3015", "")), ("AI 3015", ("AI3015", "")),
    ("AI-3015T00", ("AI3015", "T00")), ("ab-650t00", ("AB650", "T00")), ("SC-300T01", ("SC300", "T01")),
    ("3015", None), ("MSLEAIBootcampFUN", None), ("ABCDE-123", None), ("A-1", None), ("", None), (None, None),
])
def test_class_code_parsing(text, expected):
    assert parse_class_code(text) == expected


@pytest.mark.parametrize("code", ["AI-3025", "ai-3025", "AI3025", "AI%203025", "AI-3025T00", "ai3025t00"])
def test_a_class_is_found_by_any_spelling_of_its_code(client, code):
    r = client.get(f"/classes/{code}")
    assert r.status_code == 200 and r.json()["uid"] == "course.ai3025"


def test_class_returns_its_full_record_and_its_learning_modules(client, data):
    r = client.get("/classes/AI-3025").json()
    assert r["item"] == next(c for c in data["courses"] if c["uid"] == "course.ai3025")
    assert r["class_code"] == "AI-3025" and r["also_matches"] == []
    assert ids(r["learning_paths"]) == ["p.a"]
    assert r["learning_paths"][0]["item"] == next(p for p in data["learningPaths"] if p["uid"] == "p.a")
    assert ids(r["modules"]) == ["m.one", "m.two"]
    assert r["modules"][0]["item"] == next(m for m in data["modules"] if m["uid"] == "m.one")
    assert r["modules"][0]["via_learning_paths"] == ["p.a"] and r["modules"][0]["direct"] is False
    assert r["modules"][0]["link"] == "https://learn.microsoft.com/en-us/training/modules/m.one/"
    assert r["unresolved"] == [{"field": "modules", "uid": "m.missing", "in": "p.a", "reason": "not in the catalog"}]
    assert r["totals"] == {"learning_paths": 1, "modules": 2, "duration_minutes": 30, "unresolved": 1}


def test_modules_are_listed_once_in_study_guide_order_with_the_paths_they_came_through(client):
    r = client.get("/classes/SC-300").json()
    assert ids(r["modules"]) == ["m.direct", "m.one", "m.two", "m.three"]
    by = {m["uid"]: m for m in r["modules"]}
    assert (by["m.direct"]["direct"], by["m.direct"]["via_learning_paths"]) == (True, [])
    assert by["m.two"]["via_learning_paths"] == ["p.a", "p.b"]      # in both paths, listed once
    assert by["m.three"]["via_learning_paths"] == ["p.b"]
    assert ids(r["learning_paths"]) == ["p.a", "p.b"]               # p.a is in the study guide twice
    assert r["totals"] == {"learning_paths": 2, "modules": 4, "duration_minutes": 65, "unresolved": 3}
    assert {(u["uid"], u["in"], u["reason"]) for u in r["unresolved"]} == {
        ("p.gone", "course.sc300", "not in the catalog"), ("m.missing", "p.a", "not in the catalog"),
        ("exam.y", "course.sc300", "a exam is not a learning path or module")}


def test_a_class_with_no_study_guide_has_no_modules(client):
    r = client.get("/classes/XY-100").json()
    assert r["uid"] == "course.xy100a"
    c = client.get("/classes", params={"q": "bootcamp"}).json()["results"][0]
    assert c["modules"] == [] and c["totals"] == {"learning_paths": 0, "modules": 0, "duration_minutes": 0, "unresolved": 0}


def test_a_code_shared_by_two_deliveries_picks_one_and_reports_the_other(client):
    first = client.get("/classes/XY-100").json()
    assert first["uid"] == "course.xy100a" and ids(first["modules"]) == ["m.direct"]
    assert [a["uid"] for a in first["also_matches"]] == ["course.xy100b"]
    second = client.get("/classes/XY-100T01").json()
    assert second["uid"] == "course.xy100b" and [a["uid"] for a in second["also_matches"]] == ["course.xy100a"]


def test_unknown_code_gives_404_with_the_nearest_codes(client):
    r = client.get("/classes/AI-3015")
    assert r.status_code == 404
    detail = r.json()["detail"]
    assert "AI-3015" in detail["message"] and "AI-3025" in detail["message"]
    assert [s["code"] for s in detail["suggestions"]][0] == "AI-3025"
    assert detail["suggestions"][0]["reason"] == "same prefix, nearest number"
    assert detail["suggestions"][0]["link"] == "https://learn.microsoft.com/en-us/training/courses/course.ai3025/"


def test_same_number_under_another_prefix_is_suggested(client):
    s = client.get("/classes/XX-3025").json()["detail"]["suggestions"]
    assert s and s[0]["code"] == "AI-3025" and s[0]["reason"] == "same number, different prefix"


def test_something_that_is_not_a_code_gets_a_404_that_points_to_search(client):
    detail = client.get("/classes/robots").json()["detail"]
    assert detail["suggestions"] == [] and "GET /classes?q=" in detail["message"]


def test_include_modules_false_keeps_the_counts_but_drops_the_lists(client):
    r = client.get("/classes/SC-300", params={"include_modules": "false"}).json()
    assert r["modules"] == [] and r["learning_paths"] == [] and r["unresolved"] == []
    assert r["totals"]["modules"] == 4


def test_search_by_code_puts_the_class_first_and_marks_how_it_matched(client):
    r = client.get("/classes", params={"q": "AI-3025"}).json()
    assert r["query"]["code"] == "AI3025" and r["suggestions"] == []
    # the decoy class mentions "AI 3025" in its name and would sort first alphabetically; the code match still wins
    assert [(x["uid"], x["match"]) for x in r["results"]] == [("course.ai3025", "code"), ("course.decoy", "keywords")]
    top = r["results"][0]
    assert top["score"] is None and r["results"][1]["score"] > 0
    assert ids(top["modules"]) == ["m.one", "m.two"] and top["class_code"] == "AI-3025"


def test_search_by_code_that_does_not_exist_returns_suggestions_and_a_warning(client):
    r = client.get("/classes", params={"q": "AI-3015"}).json()
    assert r["total"] == 0 and r["results"] == []
    assert [s["code"] for s in r["suggestions"]][0] == "AI-3025"
    assert any("AI-3015" in w for w in r["warnings"])


def test_search_by_words_in_the_class_name(client):
    r = client.get("/classes", params={"q": "robots"}).json()
    assert [x["uid"] for x in r["results"]] == ["course.ai3025"]
    top = r["results"][0]
    assert top["match"] == "keywords" and top["score"] > 0 and top["matched_terms"] == ["robot"]
    assert client.get("/classes", params={"q": "identity access"}).json()["results"][0]["uid"] == "course.sc300"
    assert client.get("/classes", params={"q": "robots identity"}).json()["total"] == 0
    assert client.get("/classes", params={"q": "robots identity", "match": "any"}).json()["total"] == 2


def test_class_search_only_returns_classes(client):
    types = {x["type"] for x in client.get("/classes", params={"q": "copilot", "limit": 25}).json()["results"]}
    assert types == {"course"}


def test_class_search_filters_by_roles_and_levels(client):
    r = client.get("/classes", params={"q": "identity", "roles": "administrator", "limit": 25}).json()
    assert [x["uid"] for x in r["results"]] == ["course.sc300"]
    assert client.get("/classes", params={"q": "identity", "levels": "beginner"}).json()["total"] == 0
    r = client.get("/classes", params={"roles": "administrator", "limit": 25}).json()
    assert {x["uid"] for x in r["results"]} == {"course.c", "course.sc300"}
    assert client.get("/classes", params={"q": "AI-3025", "roles": "administrator"}).json()["total"] == 0   # filters also apply to code matches
    assert any("Unknown roles: wizard" in w for w in client.get("/classes", params={"roles": "wizard"}).json()["warnings"])


def test_classes_without_a_code_are_found_by_name_only(client):
    r = client.get("/classes", params={"q": "classroom stories"}).json()["results"][0]
    assert r["uid"] == "course.nocode" and r["class_code"] is None and ids(r["modules"]) == ["m.two", "m.three"]
    assert client.get("/classes", params={"q": "bootcamp"}).json()["results"][0]["class_code"] is None   # alias text is not a code
    assert client.get("/classes/course.nocode").status_code == 404


def test_listing_pages_and_limits(client):
    first = client.get("/classes", params={"limit": 2}).json()
    second = client.get("/classes", params={"limit": 2, "offset": 2}).json()
    assert first["total"] == 8 and len(first["results"]) == 2 and not set(ids(first["results"])) & set(ids(second["results"]))
    assert client.get("/classes", params={"limit": 26}).status_code == 422
    assert client.get("/classes", params={"limit": 0}).status_code == 422
    assert client.get("/classes", params={"match": "some"}).status_code == 422


def test_meta_counts_classes_with_and_without_a_code(client):
    assert client.get("/meta").json()["classes"] == {"total": 8, "with_code": 6, "without_code": 2}


def test_class_endpoints_honour_the_api_key(tmp_path, monkeypatch, data):
    with make_client(tmp_path, monkeypatch, data, api_key="s3cret") as c:
        assert c.get("/classes/AI-3025").status_code == 401
        assert c.get("/classes").status_code == 401
        assert c.get("/classes/AI-3025", headers={"x-api-key": "s3cret"}).status_code == 200


@pytest.mark.skipif(not REAL_FILE.exists(), reason="catalog/ms-learn-api.json is not present")
def test_every_real_class_returns_exactly_the_modules_its_study_guide_leads_to(tmp_path, monkeypatch):
    raw = json.loads(REAL_FILE.read_text(encoding="utf-8"))
    paths = {p["uid"]: p for p in raw["learningPaths"]}
    modules = {m["uid"]: m for m in raw["modules"]}
    coded = [c for c in raw["courses"] if parse_class_code(c["course_number"])]
    assert len(coded) >= 80

    def expected(c):          # an independent re-implementation of "the modules this class covers"
        out, via = [], {}
        for ref in c["study_guide"]:
            if ref["type"] == "learningPath" and ref["uid"] in paths:
                for m in paths[ref["uid"]]["modules"]:
                    if m in modules:
                        if m not in via:
                            out.append(m)
                        via.setdefault(m, [])
                        if ref["uid"] not in via[m]:
                            via[m].append(ref["uid"])
            elif ref["type"] == "module" and ref["uid"] in modules:
                if ref["uid"] not in via:
                    out.append(ref["uid"])
                via.setdefault(ref["uid"], [])
        return out, via

    monkeypatch.setenv("CATALOG_PATH", str(REAL_FILE))
    monkeypatch.delenv("API_KEY", raising=False)
    from app.main import app
    from fastapi.testclient import TestClient
    with TestClient(app) as c:
        assert c.get("/meta").json()["classes"] == {"total": len(raw["courses"]), "with_code": len(coded), "without_code": len(raw["courses"]) - len(coded)}
        for course_record in coded:
            number = course_record["course_number"]
            got = c.get(f"/classes/{number.lower().replace('-', '')}").json()
            want, via = expected(course_record)
            assert got["item"] == course_record, number
            assert ids(got["modules"]) == want, number
            assert {m["uid"]: m["via_learning_paths"] for m in got["modules"]} == via, number
            assert got["totals"]["duration_minutes"] == sum(modules[m]["duration_in_minutes"] for m in want), number
            assert got["modules"] == [] or all(m["item"] == modules[m["uid"]] for m in got["modules"]), number

        ab = c.get("/classes/AB-650T00").json()
        assert ab["totals"]["learning_paths"] == 3 and ab["totals"]["modules"] == 17
        assert c.get("/classes", params={"q": "AB-650"}).json()["results"][0]["uid"] == ab["uid"]
        assert c.get("/classes", params={"q": "work smarter with ai"}).json()["results"][0]["class_code"] == "AI-3025"

        missing = c.get("/classes/AI-3015")
        assert missing.status_code == 404
        assert {s["code"] for s in missing.json()["detail"]["suggestions"][:3]} == {"AI-3008", "AI-3025", "AI-3026"}
