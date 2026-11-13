# Microsoft Learn catalog search service

A small web API (FastAPI) that serves the [Microsoft Learn catalog](https://learn.microsoft.com/api/catalog/)
for keyword search. It is built to run as an Azure Container App.

- **Search by keyword**, with optional filters by **roles** and **levels** (and products and types).
- **Ranked by popularity** (highest first).
- **Returns all information**: every result carries the complete, unchanged catalog record.

The whole catalog is loaded into memory when the service starts (about 1 s, about 170 MB), so a query
takes about a millisecond. The service makes no outbound calls while running.

## API

Interactive documentation is at `/docs` and the OpenAPI schema at `/openapi.json`.

| Endpoint | What it does |
|----------|--------------|
| `GET /search` | Keyword search with optional filters, ranked by popularity |
| `GET /items/{uid}` | One complete record. Add `?expand=true` to also get the records it refers to (a learning path's modules, a module's units, a course's study guide) and the records that refer to it. References that do not exist in the catalog are listed under `unresolved` |
| `GET /taxonomies`, `GET /taxonomies/{levels\|products\|roles\|subjects}` | The valid filter ids, exactly as in the catalog file |
| `GET /meta` | What is loaded, record counts per collection, and when the catalog file was written |
| `GET /health` | Liveness and readiness probe |

### `GET /search` parameters

| Parameter | Default | Notes |
|-----------|---------|-------|
| `q` | empty | Keywords. Empty returns everything that passes the filters, most popular first |
| `roles` | none | Optional. Role ids such as `administrator`, `business-user`. Any of the listed roles matches |
| `levels` | none | Optional. `beginner`, `intermediate`, `advanced`. Any of the listed levels matches |
| `products` | none | Optional. Product ids such as `microsoft-365-copilot` |
| `types` | all except `unit` | `module`, `learningPath`, `course`, `certification`, `exam`, `appliedSkill`, `unit` |
| `match` | `all` | `all`: every keyword must match. `any`: at least one |
| `sort` | `popularity` | `popularity` or `relevance` |
| `limit`, `offset` | 10, 0 | `limit` is 1 to 100 |

`roles`, `levels`, `products` and `types` can be repeated (`roles=a&roles=b`) or comma-separated
(`roles=a,b`). Filters of different kinds are combined with AND.

```text
GET /search?q=copilot agents&roles=business-user&levels=beginner&limit=5
```

```json
{
  "query": {"q": "copilot agents", "tokens": ["copilot", "agent"], "match": "all", "sort": "popularity",
            "roles": ["business-user"], "levels": ["beginner"], "products": [], "types": []},
  "total": 49, "limit": 5, "offset": 0, "warnings": [],
  "results": [
    {"uid": "learn.dpu.…", "type": "learningPath", "collections": ["learningPaths"],
     "link": "https://learn.microsoft.com/en-us/training/paths/…/", "popularity": 0.959,
     "score": 6.0, "matched_terms": ["copilot", "agent"],
     "item": { "...the complete catalog record, unchanged..." }}
  ]
}
```

- `item` is the record exactly as it is in the catalog file (its `url` keeps the `?WT.mc_id=…` tracking
  parameter). `link` is the same URL without the query string.
- Unknown role, level or product ids do not fail the call: they return no results and a `warnings`
  entry that points to `/taxonomies/...`.

### Ranking and matching

- **Ranking:** popularity, highest first. Records without a popularity value (courses, certifications,
  exams, applied skills and units: only modules and learning paths have one) come last. Ties are broken
  by `score`, then by title.
- **Keyword matching:** case-insensitive, plurals are folded (`agents` finds `agent`) and a keyword
  matches words that start with it (`govern` finds `governance`). The keywords are looked up in the
  title, the summary (HTML removed), and the product, role, level and subject names. A few filler
  words (`the`, `for`, `microsoft`, ...) are ignored. Course numbers such as `AB-650T00` match.
- **`score`** says how well a result matches the keywords (title 3, tags 1.5, summary 1 per keyword).
  Because ranking is by popularity, a very popular loose match can outrank a closer one: look at
  `score` and `matched_terms`, or use `sort=relevance`.
- This is keyword search, not semantic search. If `match=all` finds nothing for a long phrase, try fewer
  keywords or `match=any`.

### What is in the data

All 8 collections of the catalog file are served: `modules`, `units`, `learningPaths`, `appliedSkills`,
`certifications`, `mergedCertifications`, `exams` and `courses`, plus the four taxonomies.

- The 155 certifications appear in the file twice (`certifications` and `mergedCertifications`) with the
  same uid. They are served as one record per uid, combining the fields of both. Where the two copies
  differ (the `study_guide` lists) the entries are unioned, so nothing is dropped. `collections` shows
  both sources.
- `unit` records (about 28,000 one-line lessons) are searched only when you ask for `types=unit`.
- Some uids referenced by the catalog (for example a few modules inside learning paths) do not exist in
  it. That is a property of the data; `?expand=true` reports them under `unresolved`.

## Run it locally

```powershell
cd catalog
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements-dev.txt
.\.venv\Scripts\python -m app.fetch data\ms-learn-api.json        # or put ms-learn-api.json in this folder
.\.venv\Scripts\python -m uvicorn app.main:app --port 8000
```

The catalog file is found at `CATALOG_PATH`, then `data/ms-learn-api.json`, then `ms-learn-api.json` in
this folder. Run the tests with `.\.venv\Scripts\python -m pytest`; the test that uses your real catalog
file is skipped when the file is not there.

## Container

The [Dockerfile](Dockerfile) downloads the catalog while building the image (and fails the build if the
download is incomplete), so the running container needs no internet access.

```powershell
docker build -t csm-learn-catalog .
docker run --rm -p 8000:8000 csm-learn-catalog
```

Podman works the same way (`podman build`, `podman run`). On Windows, run `podman machine init` and
`podman machine start` once first. Add `-e API_KEY=<value>` to `docker run` to require the `x-api-key`
header. Then open <http://localhost:8000/docs>.

## Deploy to Azure Container Apps

Not yet deployed. These commands use `az containerapp up`, which builds the image from the Dockerfile in
Azure Container Registry and creates the environment and the app. Run them from this folder after
`az login`:

```powershell
az group create -n rg-csm-catalog -l eastus
az containerapp up -n csm-learn-catalog -g rg-csm-catalog -l eastus --source . --ingress external --target-port 8000

# Require an API key on every call except /health (the app is open until this is done)
az containerapp secret set -n csm-learn-catalog -g rg-csm-catalog --secrets api-key=<choose-a-long-random-value>
az containerapp update -n csm-learn-catalog -g rg-csm-catalog --set-env-vars API_KEY=secretref:api-key --cpu 0.5 --memory 1.0Gi --min-replicas 1
```

Then call it with the header `x-api-key: <value>`. Set the probes to `GET /health` on port 8000. The
catalog is public Microsoft Learn data; the key only stops other people from using your capacity
(`/docs` and `/openapi.json` stay readable).

### Keeping the catalog current

The catalog is fixed when the image is built. Microsoft refreshes the source at least daily, so run
`az containerapp up ... --source .` again (for example from a weekly scheduled job) to pick up new
content. The public catalog endpoint is planned for deprecation by Microsoft; if it stops working the
build fails instead of shipping an incomplete catalog.

## Using it from Cowork

This is a plain REST API. A Cowork plugin connector needs an MCP server (Streamable HTTP), so the
service would need an MCP front end before the plugin can call it. The search logic is in
[app/catalog.py](app/catalog.py) and can be reused for that.
