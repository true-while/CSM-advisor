# Microsoft Learn catalog search service

A small web API (FastAPI) that serves the [Microsoft Learn catalog](https://learn.microsoft.com/api/catalog/)
for keyword search. It is built to run as an Azure Container App.

- **Search by keyword**, with optional filters by **roles** and **levels** (and products and types).
- **Ranked by popularity** (highest first).
- **Returns all information**: every result carries the complete, unchanged catalog record.
- **Look up a class by its code** (for example `AI-3025`) and get back the learning paths and modules it covers.

The whole catalog is loaded into memory when the service starts (about 1 s, about 170 MB), so a query
takes about a millisecond. The service makes no outbound calls while running.

## API

Interactive documentation is at `/docs` and the OpenAPI schema at `/openapi.json`.

| Endpoint | What it does |
|----------|--------------|
| `GET /search` | Keyword search with optional filters, ranked by popularity |
| `GET /classes/{code}` | One class (instructor-led course) by its code, such as `AI-3025`, with the learning paths and modules it covers. See [Classes](#classes) |
| `GET /classes` | Search classes by code or by words in the name, with their modules. See [Classes](#classes) |
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

## Classes

A class is an instructor-led course in the catalog (`courses`), identified by a code such as `AB-650T00`
or `AI-3025`. Each class has a *study guide*: the learning paths (and sometimes modules) that make it up.
The API follows that study guide and returns the learning modules the class covers.

```text
GET /classes/AI-3025
```

```json
{
  "uid": "course.ai-3025", "type": "course", "class_code": "AI-3025", "link": "https://learn.microsoft.com/en-us/training/courses/ai-3025/",
  "item": { "...the complete class record, unchanged..." },
  "learning_paths": [ { "uid": "learn.wwl.work-smarter-with-ai", "item": { "...complete record..." } } ],
  "modules": [
    { "uid": "learn.wwl.work-smarter-with-ai", "link": "https://learn.microsoft.com/en-us/training/modules/…/",
      "popularity": 0.5, "item": { "...the complete module record, unchanged..." },
      "via_learning_paths": ["learn.wwl.work-smarter-with-ai"], "direct": false }
  ],
  "unresolved": [],
  "totals": { "learning_paths": 1, "modules": 1, "duration_minutes": 42, "unresolved": 0 },
  "also_matches": []
}
```

- **Codes:** case, punctuation and the delivery suffix do not matter. `AI-3025`, `ai3025`, `AI 3025` and
  `AI-3025T00` find the same class, and `AB-650` finds `AB-650T00`. A code that exists twice (for example `T00`
  and `T01`) returns one class and lists the other in `also_matches`; naming the suffix picks that one.
- **Modules:** listed in study-guide order, each once, even when several learning paths contain it.
  `via_learning_paths` says which paths it came through, and `direct` is true when the study guide lists the
  module itself. `totals.duration_minutes` is the sum of the module durations in the catalog.
- **`unresolved`:** references in the study guide that are not in the catalog (the data has a few, for example a
  module inside a learning path that does not exist). They are listed with a reason and never guessed; the totals
  count only what resolved.
- **Not found:** an unknown code returns `404` with the nearest codes (`AI-3015` gives `AI-3008`, `AI-3025`,
  `AI-3026`, ...). Nothing is made up for a class that is not in the catalog.

`GET /classes` searches classes, using a code or words from the class name:

| Parameter | Default | Notes |
|-----------|---------|-------|
| `q` | empty | A class code, or words from the name. A class whose code equals the query comes first (`match: "code"`), then name matches by relevance (`match: "keywords"`). Empty lists all classes |
| `roles`, `levels`, `products` | none | Optional filters, as in `/search`. They also apply to a code match |
| `match` | `all` | For words: every word (`all`) or at least one (`any`) |
| `include_modules` | `true` | `false` returns the class and its `totals` without the module lists |
| `limit`, `offset` | 5, 0 | `limit` is 1 to 25 |

If `q` looks like a code that does not exist, the response has `total: 0`, a `warning`, and `suggestions` with the
nearest codes. Classes have no popularity value, so they are not ranked by popularity.

**What is in the data.** At the time of writing the catalog has about 135 classes, of which about 87 have a real code
and can be looked up by it (these numbers change as Microsoft updates the catalog; `GET /meta` shows the current
ones under `classes`). The rest, 48 at the time of writing and mostly education courses, have no code or only a text
alias such as `MSLEAIBootcampFUN`; they are found by words in their name and return `class_code: null`. The catalog
uses Microsoft Learn's own numbering, so it does not contain every class code you may have seen elsewhere (for
example `AI-3015` is not in it).

**Response size.** A class returns the complete record of every module, so one class is about 30 KB and a page of
25 is about 750 KB. Use `limit`, or `include_modules=false` and then `GET /classes/{code}` for the one you want.

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
docker run --rm -p 127.0.0.1:8000:8000 csm-learn-catalog
```

Podman works the same way (`podman build`, `podman run`). On Windows, run `podman machine init` and
`podman machine start` once first. Add `-e API_KEY=<value>` to `docker run` to require the `x-api-key`
header. Then open <http://localhost:8000/docs>.

Publish the port on `127.0.0.1` as shown. With Podman on Windows, a plain `-p 8000:8000` also listens
on IPv6, and browsers that try `localhost` over IPv6 first get `ERR_EMPTY_RESPONSE`.

## Publish the image and update the Container App

[deploy/publish-image.ps1](deploy/publish-image.ps1) builds the image, pushes it to an Azure Container
Registry, and updates the Container App `learn-catalog` (resource group `alex-app-containers`) to the new
version. Run `az login` first. You need AcrPush on the registry and Contributor on the app.

```powershell
./deploy/publish-image.ps1                         # build, publish, and deploy to the app (registry = the one the app pulls from)
./deploy/publish-image.ps1 -DryRun                 # read-only checks, then print every step
./deploy/publish-image.ps1 -NoAppUpdate -Registry <name>   # publish only
./deploy/publish-image.ps1 -Registry <name>        # publish to another registry (the app must be able to pull from it)
./deploy/publish-image.ps1 -NoParamUpdate          # do not write the new digest into main.bicepparam
./deploy/publish-image.ps1 -Tag 1.0.0 -NoLatest
./deploy/publish-image.ps1 -UseAcrBuild            # build inside the registry; no local container runtime
./deploy/publish-image.ps1 -AppName <app> -AppResourceGroup <rg> -AppSubscription <id> -RegistrySubscription <id>
```

What it does, in order:

1. **Preflight (read-only, before building).** Reads the app, takes the registry from it (unless `-Registry`
   is given), and decides how the app will pull the image (see below). It stops here if the app cannot pull,
   so a long build is not wasted.
2. **Builds** with Docker or Podman, with a new `CATALOG_REFRESH` build argument each run so the image
   contains a freshly downloaded catalog instead of one cached from an earlier build.
3. **Signs in** with a short-lived Microsoft Entra token (the registry's admin user stays disabled and no
   password is stored) and **pushes** an immutable tag (`<yyyyMMdd>-<git sha>`, with `-dirty` if the folder
   has uncommitted changes) and, unless `-NoLatest` is given, `latest`. It refuses to overwrite a tag.
4. **Updates the app to the image digest** (`<server>/csm-learn-catalog@sha256:...`), so a later `latest`
   push cannot change what is running. It waits for the new revision to be healthy, then calls the app's
   `/health` and `/meta` and checks that it is serving the catalog downloaded by this run.
5. **Updates [deploy/main.bicepparam](deploy/main.bicepparam)** with the new digest, so a later redeploy of the
   Bicep template does not roll the app back. It only does this when the file is for the same app and
   registry, and only after the new revision is healthy. Commit the change. Use `-NoParamUpdate` to skip it.
6. **Prints the previous image** and the command to roll back to it. A moving tag such as `latest` is
   resolved to its digest before the push, because this run moves the tag; the rollback command uses
   the digest.

In Single revision mode the previous revision keeps serving traffic until the new one is healthy, so an
image that fails to start does not take the app down.

### How the app pulls from the registry

| Situation | What the script does |
|-----------|----------------------|
| The app already has access to the registry (for example an app deployed with [deploy/main.bicep](deploy/main.bicep), which pulls with a user-assigned managed identity) | Keeps it as it is |
| Not configured, and the app and the registry are in the same Microsoft Entra tenant | Uses the app's user-assigned managed identity (if it has exactly one) or enables its system-assigned identity, grants it **AcrPull** on the registry, and configures the app to use it. Needs permission to create role assignments (Owner or User Access Administrator). A new role assignment can take a minute or two, so the script retries |
| Not configured, and they are in different tenants | Stops before building. A managed identity cannot be granted access across tenants. Publish to a registry the app already pulls from (`-Registry`), or give the app credentials for the registry first (`az containerapp registry set ... --username ... --password ...`) |

The script selects subscriptions per command (`--subscription`) and does not change your default Azure
CLI subscription. Use `-RegistrySubscription` and `-AppSubscription` if the two are in different
subscriptions. The Azure CLI must be signed in to every tenant involved.

The repository is `csm-learn-catalog`. Other repositories in the registry are not touched.

## A stable URL (Bicep)

The app's URL is `https://<app name>.<environment default domain>`, for example
`https://learn-catalog.yellowgrass-5e694844.eastus2.azurecontainerapps.io`. No domain registration is needed.

The default domain is generated **once, when the Container Apps environment is created**, and then never
changes. So the URL stays the same through new image versions, new revisions, scaling, and even deleting and
recreating the app, as long as:

1. the **environment is kept**, and
2. the app keeps its **name**.

It changes only if the environment is deleted and recreated, or the app is renamed. Each revision also has its
own address (`<app>--<revision>.<domain>`), which does change; use the plain app URL.

[deploy/main.bicep](deploy/main.bicep) deploys the app with that in mind:

- It deploys **into the existing environment** (`createEnvironment = false` by default), so the domain is kept.
- It puts a **delete lock** on the environment, so the domain cannot be lost by accident. The lock still
  allows updates. Remove it first (`az lock delete`) if you really want to delete the environment.
- The app pulls its image with a **user-assigned managed identity** that gets the **AcrPull** role on the
  registry, so there is no registry password. The registry must be in the same Microsoft Entra tenant.
- Ingress on port 8000, `/health` liveness and readiness probes, a single active revision (the previous
  revision keeps serving until the new one is healthy).
- Optional API key: set the `CATALOG_API_KEY` environment variable before deploying. Clients then send the
  `x-api-key` header; `/health` stays open. Empty means no key.

Edit [deploy/main.bicepparam](deploy/main.bicepparam) (app name, environment, registry, image digest), then:

```powershell
cd catalog/deploy
az deployment group what-if -g <resource-group> -f main.bicep -p main.bicepparam   # preview, changes nothing
az deployment group create  -g <resource-group> -f main.bicep -p main.bicepparam
```

The deployment prints the `url`. To deploy a different image, pass it on the command line
(`-p image=<registry>.azurecr.io/csm-learn-catalog@sha256:...`); `publish-image.ps1` prints the digest.
`publish-image.ps1` updates the running app directly and then writes the new digest into `main.bicepparam`
(commit it), so redeploying the template keeps the version the script deployed. If you used `-NoParamUpdate`,
or the file is not committed, give the template the digest that is currently running
(`az containerapp show -n <app> -g <rg> --query properties.template.containers[0].image`), or it will go back
to the digest in the parameter file.

**First-time deployment** into a resource group that has no environment: add `-p createEnvironment=true`. The
template then creates the environment (and a Log Analytics workspace) and the URL's domain is generated at that
moment. Re-running it later with `true` for the same group and name keeps the same environment, and the same
domain.

**Notes**

- The first deployment creates the AcrPull role assignment and starts the app straight away. A new role can take
  a minute or two to take effect, so if the first revision fails to pull the image, run the deployment again.
- The identity has no secrets: the template is safe to keep in source control.
- Needs permission to create role assignments on the registry (Owner or User Access Administrator).
- To use a registry in another tenant (for example when `az` is signed in to a different one), the app needs a
  registry username and password instead of a managed identity. This template does not support that.

### Creating the app without Bicep

The script updates an existing app. To create one by hand, use `az containerapp create` with ingress on port
8000, for example with an API key (clients then send the header `x-api-key`; `/health` stays open):

```powershell
az containerapp create -n <app> -g <rg> --environment <environment> `
  --image "<registry>.azurecr.io/csm-learn-catalog:latest" --registry-server "<registry>.azurecr.io" `
  --registry-identity system --ingress external --target-port 8000 --cpu 0.5 --memory 1.0Gi --min-replicas 1 `
  --secrets api-key=<choose-a-long-random-value> --env-vars API_KEY=secretref:api-key
```

Then grant the app's identity AcrPull on the registry, as described above.

### Keeping the catalog current

The catalog is fixed when the image is built. Microsoft refreshes the source at least daily, so run
`publish-image.ps1` again (for example from a weekly scheduled job) to publish a new image and update the
app. The public catalog endpoint is planned for deprecation by Microsoft; if it stops working the build
fails instead of shipping an incomplete catalog.

## Using it from Cowork

This is a plain REST API. A Cowork plugin connector needs an MCP server (Streamable HTTP), so the
service would need an MCP front end before the plugin can call it. The search logic is in
[app/catalog.py](app/catalog.py) and can be reused for that.
