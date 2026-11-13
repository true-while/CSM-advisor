import copy
import json
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

REAL_FILE = Path(__file__).resolve().parent.parent / "ms-learn-api.json"

FIXTURE = {
    "modules": [
        {"uid": "learn.m.copilot-basics", "type": "module", "title": "Copilot basics for everyone",
         "summary": "Learn to use Microsoft 365 Copilot agents.", "levels": ["beginner"], "roles": ["business-user"],
         "products": ["microsoft-365-copilot"], "subjects": ["artificial-intelligence"], "duration_in_minutes": 30,
         "popularity": 0.9, "url": "https://learn.microsoft.com/en-us/training/modules/copilot-basics/?WT.mc_id=api",
         "units": ["learn.m.copilot-basics.intro", "learn.m.copilot-basics.missing-unit"], "number_of_children": 2,
         "rating": {"count": 10, "average": 4.5}},
        {"uid": "learn.m.copilot-admin", "type": "module", "title": "Administer Copilot",
         "summary": "Govern and secure Copilot deployments.", "levels": ["intermediate"], "roles": ["administrator"],
         "products": ["microsoft-365-copilot"], "duration_in_minutes": 60, "popularity": 0.3,
         "url": "https://learn.microsoft.com/en-us/training/modules/copilot-admin/?WT.mc_id=api", "units": []},
        {"uid": "learn.m.sql", "type": "module", "title": "Query a database with SQL",
         "summary": "Write queries.", "levels": ["beginner", "intermediate"], "roles": ["developer", "administrator"],
         "products": ["azure-sql"], "popularity": 0.6,
         "url": "https://learn.microsoft.com/en-us/training/modules/sql/?WT.mc_id=api", "units": []},
        {"uid": "learn.m.copilot-nopop", "type": "module", "title": "Copilot extras", "summary": "More.",
         "levels": ["beginner"], "roles": ["business-user"], "products": ["microsoft-365-copilot"],
         "url": "https://learn.microsoft.com/x/?WT.mc_id=api", "units": []},
    ],
    "units": [{"uid": "learn.m.copilot-basics.intro", "type": "unit", "title": "Introduction to Copilot",
               "duration_in_minutes": 2, "locale": "en-us", "last_modified": "2026-01-01T00:00:00+00:00"}],
    "learningPaths": [
        {"uid": "learn.p.copilot", "type": "learningPath", "title": "Get started with Copilot",
         "summary": "A path.", "levels": ["beginner"], "roles": ["business-user"], "products": ["microsoft-365-copilot"],
         "popularity": 0.5, "url": "https://learn.microsoft.com/en-us/training/paths/copilot/?WT.mc_id=api",
         "modules": ["learn.m.copilot-basics", "learn.m.copilot-admin", "learn.m.gone"]},
    ],
    "appliedSkills": [],
    "certifications": [
        {"uid": "certification.x", "type": "cert", "title": "Copilot Expert", "subtitle": "Certified", "url": "https://x/?a=1",
         "levels": ["intermediate"], "roles": ["administrator"], "exams": ["exam.y"], "certification_type": "role-based",
         "study_guide": [{"uid": "learn.p.copilot", "type": "learningPath"}]},
    ],
    "mergedCertifications": [
        {"uid": "certification.x", "type": "cert", "title": "Copilot Expert", "summary": "Cert summary", "url": "https://x/?a=1",
         "levels": ["intermediate"], "roles": ["administrator"], "products": ["microsoft-365-copilot"],
         "skills": ["Deploy governance controls"], "certification_type": "role-based",
         "study_guide": [{"uid": "course.c", "type": "course"}]},
    ],
    "exams": [{"uid": "exam.y", "type": "exam", "title": "Exam Y", "display_name": "Y", "levels": ["intermediate"],
               "roles": ["administrator"], "products": ["microsoft-365-copilot"], "url": "https://y/", "courses": [], "study_guide": []}],
    "courses": [{"uid": "course.c", "type": "course", "course_number": "AB-650T00", "title": "Administer Microsoft 365 and AI",
                 "summary": "<p>Course for <b>admins</b>.</p>", "levels": ["intermediate"], "roles": ["administrator"],
                 "products": ["microsoft-365-copilot"], "duration_in_hours": 24, "url": "https://c/?a=1",
                 "study_guide": [{"uid": "learn.p.copilot", "type": "learningPath"}], "recommendation_list": []}],
    "levels": [{"id": "beginner", "name": "Beginner"}, {"id": "intermediate", "name": "Intermediate"},
               {"id": "advanced", "name": "Advanced"}],
    "products": [{"id": "microsoft-365-copilot", "name": "Microsoft 365 Copilot", "children": []},
                 {"id": "azure-sql", "name": "Azure SQL", "children": []}],
    "roles": [{"id": "administrator", "name": "Administrator"}, {"id": "business-user", "name": "Business User"},
              {"id": "developer", "name": "Developer"}],
    "subjects": [{"id": "artificial-intelligence", "name": "Artificial intelligence", "children": []}],
}


def make_client(tmp_path, monkeypatch, data=FIXTURE, api_key=None):
    path = tmp_path / "catalog.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    monkeypatch.setenv("CATALOG_PATH", str(path))
    if api_key:
        monkeypatch.setenv("API_KEY", api_key)
    else:
        monkeypatch.delenv("API_KEY", raising=False)
    from app.main import app
    return TestClient(app)


@pytest.fixture()
def client(tmp_path, monkeypatch):
    with make_client(tmp_path, monkeypatch) as c:
        yield c


def uids(response):
    return [r["uid"] for r in response.json()["results"]]


def test_results_are_ranked_by_popularity_and_items_without_popularity_come_last(client):
    r = client.get("/search", params={"q": "copilot", "types": "module"})
    assert r.status_code == 200
    assert uids(r) == ["learn.m.copilot-basics", "learn.m.copilot-admin", "learn.m.copilot-nopop"]


def test_all_types_are_searched_by_default_but_units_are_not(client):
    r = client.get("/search", params={"q": "copilot"})
    types = {x["type"] for x in r.json()["results"]}
    assert {"module", "learningPath", "course", "certification", "exam"} <= types
    assert "unit" not in types
    assert uids(client.get("/search", params={"q": "introduction", "types": "unit"})) == ["learn.m.copilot-basics.intro"]


def test_filter_by_roles_and_levels(client):
    r = client.get("/search", params={"q": "copilot", "types": "module", "roles": "administrator"})
    assert uids(r) == ["learn.m.copilot-admin"]
    r = client.get("/search", params={"q": "copilot", "types": "module", "levels": "beginner"})
    assert uids(r) == ["learn.m.copilot-basics", "learn.m.copilot-nopop"]
    r = client.get("/search", params={"q": "copilot", "types": "module", "levels": "beginner", "roles": "administrator"})
    assert uids(r) == []


def test_repeated_and_comma_separated_filters_are_equivalent(client):
    a = client.get("/search", params=[("roles", "developer"), ("roles", "administrator"), ("types", "module")])
    b = client.get("/search", params={"roles": "developer,administrator", "types": "module"})
    assert uids(a) == uids(b) == ["learn.m.sql", "learn.m.copilot-admin"]


def test_unknown_filter_values_produce_a_warning_not_an_error(client):
    r = client.get("/search", params={"q": "copilot", "roles": "wizard"})
    assert r.status_code == 200 and r.json()["total"] == 0
    assert any("Unknown roles: wizard" in w for w in r.json()["warnings"])


def test_keywords_match_all_by_default_and_any_on_request(client):
    assert uids(client.get("/search", params={"q": "copilot sql", "types": "module"})) == []
    r = client.get("/search", params={"q": "copilot sql", "types": "module", "match": "any"})
    assert uids(r)[0] == "learn.m.copilot-basics" and "learn.m.sql" in uids(r)


def test_plurals_prefixes_html_and_course_numbers(client):
    assert "learn.m.copilot-basics" in uids(client.get("/search", params={"q": "agent"}))
    assert "learn.m.copilot-admin" in uids(client.get("/search", params={"q": "govern secur"}))
    assert uids(client.get("/search", params={"q": "AB-650T00"})) == ["course.c"]
    assert uids(client.get("/search", params={"q": "admins", "types": "course"})) == ["course.c"]


def test_relevance_sort_puts_title_matches_first(client):
    r = client.get("/search", params={"q": "copilot administer", "match": "any", "sort": "relevance", "types": "module"})
    assert uids(r)[0] == "learn.m.copilot-admin"


def test_empty_query_browses_by_popularity_and_paginates(client):
    first = client.get("/search", params={"types": "module", "limit": 2}).json()
    assert first["total"] == 4 and [r["uid"] for r in first["results"]] == ["learn.m.copilot-basics", "learn.m.sql"]
    second = client.get("/search", params={"types": "module", "limit": 2, "offset": 2}).json()
    assert [r["uid"] for r in second["results"]] == ["learn.m.copilot-admin", "learn.m.copilot-nopop"]


def test_results_carry_the_complete_record_unchanged(client):
    result = client.get("/search", params={"q": "copilot basics"}).json()["results"][0]
    assert result["item"] == FIXTURE["modules"][0]
    assert result["link"] == "https://learn.microsoft.com/en-us/training/modules/copilot-basics/"
    assert result["item"]["url"].endswith("?WT.mc_id=api")


def test_duplicate_certification_records_are_merged_without_losing_fields(client):
    item = client.get("/items/certification.x").json()
    assert item["collections"] == ["certifications", "mergedCertifications"]
    assert {"subtitle", "exams", "summary", "skills"} <= set(item["item"])
    assert item["item"]["study_guide"] == [{"uid": "learn.p.copilot", "type": "learningPath"},
                                            {"uid": "course.c", "type": "course"}]
    assert uids(client.get("/search", params={"types": "certification"})) == ["certification.x"]


def test_item_lookup_and_expand_report_unresolved_references(client):
    assert client.get("/items/nope").status_code == 404
    path = client.get("/items/learn.p.copilot", params={"expand": "true"}).json()
    assert [m["uid"] for m in path["expanded"]["resolved"]["modules"]] == ["learn.m.copilot-basics", "learn.m.copilot-admin"]
    assert path["expanded"]["unresolved"] == [{"field": "modules", "uid": "learn.m.gone"}]
    assert {r["uid"] for r in path["expanded"]["referenced_by"]} == {"certification.x", "course.c"}
    module = client.get("/items/learn.m.copilot-basics", params={"expand": "true"}).json()
    assert [r["uid"] for r in module["expanded"]["referenced_by"]] == ["learn.p.copilot"]
    assert module["expanded"]["unresolved"] == [{"field": "units", "uid": "learn.m.copilot-basics.missing-unit"}]
    assert client.get("/items/learn.p.copilot").json()["expanded"] is None


def test_taxonomies_meta_and_health(client):
    assert client.get("/taxonomies").json()["levels"] == FIXTURE["levels"]
    assert client.get("/taxonomies/roles").json() == FIXTURE["roles"]
    assert client.get("/taxonomies/bogus").status_code == 422
    meta = client.get("/meta").json()
    assert meta["merged_duplicate_uids"] == 1 and meta["collections"]["modules"] == 4
    assert client.get("/health").json() == {"status": "ok", "records": meta["records"]}


def test_invalid_parameters_are_rejected(client):
    assert client.get("/search", params={"limit": 0}).status_code == 422
    assert client.get("/search", params={"limit": 101}).status_code == 422
    assert client.get("/search", params={"types": "bogus"}).status_code == 422
    assert client.get("/search", params={"match": "some"}).status_code == 422


def test_api_key_is_enforced_when_configured(tmp_path, monkeypatch):
    with make_client(tmp_path, monkeypatch, api_key="s3cret") as c:
        assert c.get("/health").status_code == 200
        assert c.get("/search").status_code == 401
        assert c.get("/search", headers={"x-api-key": "wrong"}).status_code == 401
        assert c.get("/search", headers={"x-api-key": "s3cret"}).status_code == 200


def test_a_uid_shared_by_two_types_keeps_the_first_and_reports_the_other(tmp_path, monkeypatch):
    data = copy.deepcopy(FIXTURE)
    data["exams"].append({"uid": "learn.m.sql", "type": "exam", "title": "Clash"})
    with make_client(tmp_path, monkeypatch, data) as c:
        assert c.get("/items/learn.m.sql").json()["type"] == "module"
        assert c.get("/meta").json()["skipped_records"] == [
            {"uid": "learn.m.sql", "collection": "exams", "reason": "uid used by another type"}]


@pytest.mark.skipif(not REAL_FILE.exists(), reason="catalog/ms-learn-api.json is not present")
def test_real_catalog_returns_every_record_unchanged_and_finds_the_obvious_module(tmp_path, monkeypatch):
    raw = json.loads(REAL_FILE.read_text(encoding="utf-8"))
    monkeypatch.setenv("CATALOG_PATH", str(REAL_FILE))
    monkeypatch.delenv("API_KEY", raising=False)
    from app.main import app
    with TestClient(app) as c:
        meta = c.get("/meta").json()
        assert meta["collections"] == {k: len(raw[k]) for k in meta["collections"]}
        assert meta["records"] == sum(meta["collections"].values()) - meta["merged_duplicate_uids"]
        sample = [raw["modules"][0], raw["learningPaths"][5], raw["courses"][3], raw["exams"][2], raw["appliedSkills"][1], raw["units"][10]]
        for rec in sample:
            assert c.get(f"/items/{rec['uid']}").json()["item"] == rec
        r = c.get("/search", params={"q": "copilot readiness rollout", "levels": "intermediate", "limit": 5}).json()
        assert "learn.wwl.enable-manage-microsoft-365-copilot" in [x["uid"] for x in r["results"]]
        pops = [x["popularity"] for x in c.get("/search", params={"q": "copilot", "limit": 50}).json()["results"]
                if x["popularity"] is not None]
        assert len(pops) > 10 and pops == sorted(pops, reverse=True)
        r = c.get("/search", params={"q": "copilot", "roles": "administrator", "levels": "beginner", "limit": 50}).json()
        assert r["results"] and all("beginner" in x["item"]["levels"] and "administrator" in x["item"]["roles"]
                                    for x in r["results"])
