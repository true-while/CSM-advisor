"""HTTP API for searching the Microsoft Learn catalog. Run: uvicorn app.main:app"""
from __future__ import annotations

import hmac
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Literal

from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException, Query, Request
from pydantic import BaseModel

from .catalog import TAXONOMIES, Catalog

ROOT = Path(__file__).resolve().parent.parent
ItemType = Literal["module", "unit", "learningPath", "appliedSkill", "certification", "exam", "course"]


def catalog_path() -> Path:
    if os.environ.get("CATALOG_PATH"):
        return Path(os.environ["CATALOG_PATH"])
    for candidate in (ROOT / "data" / "ms-learn-api.json", ROOT / "ms-learn-api.json"):
        if candidate.exists():
            return candidate
    raise RuntimeError("Catalog file not found: set CATALOG_PATH or run 'python -m app.fetch'")


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.catalog = Catalog.load(catalog_path())
    yield


app = FastAPI(
    title="Microsoft Learn catalog search",
    version="1.1.0",
    description=(
        "Keyword search over the Microsoft Learn catalog (modules, learning paths, courses, "
        "certifications, exams, applied skills, units), with optional filters by roles and levels. "
        "Results are ranked by popularity and carry the complete catalog record. "
        "Classes (instructor-led courses) can be looked up by code, such as AI-3025, and return the learning "
        "paths and modules they cover."
    ),
    lifespan=lifespan,
)


def get_catalog(request: Request) -> Catalog:
    return request.app.state.catalog


def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    """When the API_KEY environment variable is set, every call except /health must send it."""
    expected = os.environ.get("API_KEY")
    if expected and not (x_api_key and hmac.compare_digest(x_api_key, expected)):
        raise HTTPException(status_code=401, detail="Missing or invalid x-api-key header")


class Item(BaseModel):
    uid: str
    type: str
    collections: list[str]
    link: str
    popularity: float | None
    item: dict[str, Any]


class Result(Item):
    score: float
    matched_terms: list[str]


class QueryInfo(BaseModel):
    q: str | None
    tokens: list[str]
    match: str
    sort: str
    roles: list[str]
    levels: list[str]
    products: list[str]
    types: list[str]


class SearchResponse(BaseModel):
    query: QueryInfo
    total: int
    limit: int
    offset: int
    warnings: list[str]
    results: list[Result]


class Reference(BaseModel):
    uid: str
    type: str
    title: str
    link: str


class Expanded(BaseModel):
    resolved: dict[str, list[Item]]
    unresolved: list[dict[str, str]]
    referenced_by: list[Reference]


class ItemDetail(Item):
    expanded: Expanded | None = None


class ClassModule(Item):
    """A learning module that belongs to a class."""
    via_learning_paths: list[str]
    direct: bool


class ClassTotals(BaseModel):
    learning_paths: int
    modules: int
    duration_minutes: int
    unresolved: int


class ClassContents(BaseModel):
    class_code: str | None
    learning_paths: list[Item]
    modules: list[ClassModule]
    unresolved: list[dict[str, str]]
    totals: ClassTotals


class ClassDetail(Item, ClassContents):
    also_matches: list[Reference]


class ClassResult(Item, ClassContents):
    match: Literal["code", "keywords"]
    score: float | None
    matched_terms: list[str]


class ClassSuggestion(BaseModel):
    uid: str
    code: str
    title: str
    link: str
    reason: str


class ClassQuery(BaseModel):
    q: str | None
    tokens: list[str]
    code: str | None
    match: str
    roles: list[str]
    levels: list[str]
    products: list[str]
    include_modules: bool


class ClassSearchResponse(BaseModel):
    query: ClassQuery
    total: int
    limit: int
    offset: int
    warnings: list[str]
    suggestions: list[ClassSuggestion]
    results: list[ClassResult]


def _class_payload(catalog: Catalog, entry, include_modules: bool) -> dict[str, Any]:
    contents = catalog.class_contents(entry)
    if not include_modules:
        contents = {**contents, "learning_paths": [], "modules": [], "unresolved": []}
    code = str(entry.item.get("course_number") or "")
    return {**catalog.wrap(entry), "class_code": code if entry.class_key else None, **contents}


def _split(values: list[str]) -> list[str]:
    """Accept repeated parameters and comma-separated lists: roles=a&roles=b or roles=a,b."""
    return list(dict.fromkeys(v.strip().lower() for value in values for v in value.split(",") if v.strip()))


router = APIRouter(dependencies=[Depends(require_api_key)])


@router.get("/search", response_model=SearchResponse, summary="Search by keyword")
def search(
    catalog: Catalog = Depends(get_catalog),
    q: str | None = Query(None, max_length=300, description="Keywords. Leave empty to browse by popularity."),
    roles: list[str] = Query([], description="Optional. Role ids (see /taxonomies/roles). Any of them matches."),
    levels: list[str] = Query([], description="Optional. beginner, intermediate, advanced. Any of them matches."),
    products: list[str] = Query([], description="Optional. Product ids (see /taxonomies/products)."),
    types: list[ItemType] = Query([], description="Optional. Default is every type except unit."),
    match: Literal["all", "any"] = Query("all", description="all = every keyword must match; any = at least one."),
    sort: Literal["popularity", "relevance"] = Query("popularity", description="Ranking order."),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> SearchResponse:
    roles, levels, products = _split(roles), _split(levels), _split(products)
    tokens, total, results = catalog.search(
        q, roles=roles, levels=levels, products=products, types=types,
        match=match, sort=sort, limit=limit, offset=offset,
    )
    return SearchResponse(
        query=QueryInfo(q=q, tokens=tokens, match=match, sort=sort, roles=roles, levels=levels,
                        products=products, types=list(types)),
        total=total, limit=limit, offset=offset,
        warnings=catalog.warnings_for(roles, levels, products),
        results=results,
    )


@router.get("/items/{uid}", response_model=ItemDetail, summary="Get one record by uid")
def get_item(uid: str, expand: bool = Query(False, description="Also return the records this one refers to."),
             catalog: Catalog = Depends(get_catalog)) -> ItemDetail:
    entry = catalog.get(uid)
    if entry is None:
        raise HTTPException(status_code=404, detail=f"No record with uid '{uid}'. uids are case-sensitive.")
    detail = catalog.wrap(entry)
    if expand:
        detail["expanded"] = catalog.expand(entry)
    return ItemDetail(**detail)


@router.get("/classes", response_model=ClassSearchResponse, summary="Search classes by code or name, with their learning modules")
def search_classes(
    catalog: Catalog = Depends(get_catalog),
    q: str | None = Query(None, max_length=300, description="A class code such as AI-3025 (case, punctuation and the T00 suffix "
                          "do not matter) or words from the class name. A class whose code equals the query comes first. "
                          "Empty lists all classes."),
    roles: list[str] = Query([], description="Optional. Role ids (see /taxonomies/roles). Any of them matches."),
    levels: list[str] = Query([], description="Optional. beginner, intermediate, advanced. Any of them matches."),
    products: list[str] = Query([], description="Optional. Product ids (see /taxonomies/products)."),
    match: Literal["all", "any"] = Query("all", description="For words in a name: all = every word must match; any = at least one."),
    include_modules: bool = Query(True, description="Include the learning paths and modules of each class."),
    limit: int = Query(5, ge=1, le=25),
    offset: int = Query(0, ge=0),
) -> ClassSearchResponse:
    roles, levels, products = _split(roles), _split(levels), _split(products)
    tokens, code, total, page, suggestions = catalog.find_classes(
        q, roles=roles, levels=levels, products=products, match=match, limit=limit, offset=offset)
    warnings = catalog.warnings_for(roles, levels, products)
    if suggestions:
        warnings.append(f"No class has the code {q!r}. See suggestions for the nearest codes.")
    results = [
        {**_class_payload(catalog, e, include_modules), "match": kind,
         "score": None if score is None else round(score, 2), "matched_terms": matched}
        for e, score, matched, kind in page
    ]
    return ClassSearchResponse(
        query=ClassQuery(q=q, tokens=tokens, code=code, match=match, roles=roles, levels=levels, products=products,
                         include_modules=include_modules),
        total=total, limit=limit, offset=offset, warnings=warnings, suggestions=suggestions, results=results)


@router.get("/classes/{code}", response_model=ClassDetail, summary="Get one class by its code, with its learning modules")
def get_class(code: str, include_modules: bool = Query(True, description="Include the learning paths and modules."),
              catalog: Catalog = Depends(get_catalog)) -> ClassDetail:
    entry, others = catalog.find_class(code)
    if entry is None:
        suggestions = catalog.suggest_classes(code)
        message = f"No class has the code '{code}'."
        if suggestions:
            message += " Nearest codes: " + ", ".join(s["code"] for s in suggestions) + "."
        else:
            message += " Search by name with GET /classes?q=..."
        raise HTTPException(status_code=404, detail={"message": message, "suggestions": suggestions})
    payload = _class_payload(catalog, entry, include_modules)
    payload["also_matches"] = [{"uid": o.uid, "type": o.type, "title": o.title, "link": o.link} for o in others]
    return ClassDetail(**payload)


@router.get("/taxonomies", summary="Levels, products, roles and subjects, as in the catalog file")
def taxonomies(catalog: Catalog = Depends(get_catalog)) -> dict[str, Any]:
    return catalog.taxonomies


@router.get("/taxonomies/{name}", summary="One taxonomy")
def taxonomy(name: Literal[TAXONOMIES], catalog: Catalog = Depends(get_catalog)) -> list[dict[str, Any]]:  # type: ignore[valid-type]
    return catalog.taxonomies[name]


@router.get("/meta", summary="What is loaded, and when the catalog file was written")
def meta(catalog: Catalog = Depends(get_catalog)) -> dict[str, Any]:
    return catalog.meta()


app.include_router(router)


@app.get("/health", summary="Liveness and readiness probe")
def health(catalog: Catalog = Depends(get_catalog)) -> dict[str, Any]:
    return {"status": "ok", "records": len(catalog.entries)}
