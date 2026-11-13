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
    version="1.0.0",
    description=(
        "Keyword search over the Microsoft Learn catalog (modules, learning paths, courses, "
        "certifications, exams, applied skills, units), with optional filters by roles and levels. "
        "Results are ranked by popularity and carry the complete catalog record."
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
