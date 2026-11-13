<#
.SYNOPSIS
    Builds the catalog search image, publishes it to an Azure Container Registry, and updates the
    Azure Container App to the new version.

.DESCRIPTION
    1. Preflight (read-only, before anything is built): finds the registry and the Container App and works out
       how the app will pull the image. It stops early if the app cannot pull from the registry.
    2. Builds the image from catalog/Dockerfile with Docker or Podman (auto-detected), or inside the registry
       with ACR Tasks (-UseAcrBuild).
    3. Signs in to the registry with a short-lived Microsoft Entra token (no admin user, no stored password)
       and pushes an immutable tag (<yyyyMMdd>-<git sha>, "-dirty" for uncommitted changes) and, unless
       -NoLatest is given, "latest".
    4. Updates the Container App to the pushed image BY DIGEST, waits for the new revision to become healthy,
       and checks the app's /health and /meta endpoints. In Single revision mode the previous revision keeps
       serving traffic until the new one is healthy, so a bad image does not take the app down.
    5. Keeps deploy/main.bicepparam in sync: writes the deployed image digest into its `image` parameter, so a later
       redeploy of the Bicep template does not roll the app back. Skip with -NoParamUpdate. Commit the change.
    6. Prints the previous image and the command to roll back to it.

    Which registry: by default the one the app already pulls from (-Registry overrides it). With -NoAppUpdate there
    is no app to read it from, so -Registry is required.

    How the app pulls from the registry:
      - The app already has credentials for the registry         -> they are used as they are (this is the normal case
                                                                      for an app deployed with deploy/main.bicep, which
                                                                      pulls with a user-assigned managed identity).
      - Not configured, and the app and registry share a tenant   -> the script uses the app's user-assigned managed
                                                                      identity (if it has exactly one) or enables its
                                                                      system-assigned identity, grants it AcrPull on
                                                                      the registry, and configures the app to use it.
      - Not configured, and they are in different tenants          -> the script stops before building. A managed
                                                                      identity cannot be granted access across
                                                                      tenants. Use a registry the app already pulls
                                                                      from, or configure credentials on the app.

    The catalog is downloaded while the image builds, so the image also carries a fresh catalog snapshot.
    Subscriptions are selected per command (--subscription); your default Azure CLI subscription is not changed.
    Run `az login` first. You need AcrPush on the registry and Contributor on the app; for the managed identity
    route you also need permission to create role assignments (Owner or User Access Administrator).

.EXAMPLE
    ./publish-image.ps1
    Builds, publishes to the registry the app pulls from, and updates the app.
.EXAMPLE
    ./publish-image.ps1 -Registry eshopacr
.EXAMPLE
    ./publish-image.ps1 -NoAppUpdate -Registry eshopacr
.EXAMPLE
    ./publish-image.ps1 -DryRun
.EXAMPLE
    ./publish-image.ps1 -RegistrySubscription <id> -AppSubscription <id> -UseAcrBuild
#>
[CmdletBinding()]
param(
    [string] $Registry,
    [Alias("Subscription")] [string] $RegistrySubscription,
    [string] $Repository = "csm-learn-catalog",
    [string] $Tag,
    [ValidateSet("auto", "docker", "podman")] [string] $Runtime = "auto",
    [switch] $UseAcrBuild,
    [switch] $NoLatest,

    [string] $AppName = "learn-catalog",
    [string] $AppResourceGroup = "alex-app-containers",
    [string] $AppSubscription,
    [switch] $NoAppUpdate,
    [ValidateRange(1, 60)] [int] $TimeoutMinutes = 8,

    [string] $ParamFile = (Join-Path $PSScriptRoot "main.bicepparam"),
    [switch] $NoParamUpdate,

    [switch] $DryRun
)

$ErrorActionPreference = "Stop"
$contextDir = Split-Path -Parent $PSScriptRoot
$startedUtc = (Get-Date).ToUniversalTime()

function Step($text) { Write-Host "`n==> $text" -ForegroundColor Cyan }
function Info($text) { Write-Host "  $text" }
function SubArgs($subscription) { if ($subscription) { return @("--subscription", $subscription) } }

# Runs a native command and returns its stdout (with -Capture), failing on a non-zero exit code.
# -ReadOnly commands also run during -DryRun; everything else is only printed.
# Windows PowerShell 5.1 turns native stderr into errors, so ErrorActionPreference is relaxed around the call.
function Invoke-Native {
    param([string] $Exe, [string[]] $Arguments, [switch] $Capture, [switch] $ReadOnly, [switch] $AllowFailure, [string] $StdIn)
    $Arguments = @($Arguments | Where-Object { $_ })
    Write-Host ("  > {0} {1}" -f (Split-Path $Exe -Leaf), (($Arguments | ForEach-Object { if ($_ -match "\s") { '"{0}"' -f $_ } else { $_ } }) -join " ")) -ForegroundColor DarkGray
    if ($DryRun -and -not $ReadOnly) { if ($Capture) { return "(dry run)" } else { return } }
    $prev = $ErrorActionPreference; $ErrorActionPreference = "Continue"
    try {
        if ($StdIn) { $out = $StdIn | & $Exe @Arguments 2>&1 } else { $out = & $Exe @Arguments 2>&1 }
        $code = $LASTEXITCODE
    } finally { $ErrorActionPreference = $prev }
    $text = ($out | ForEach-Object { "$_" }) -join "`n"
    $stdout = ($out | Where-Object { $_ -isnot [System.Management.Automation.ErrorRecord] } | ForEach-Object { "$_" }) -join "`n"
    if ($code -ne 0) {
        if ($AllowFailure) { if ($Capture) { return $null } else { return $false } }
        throw "'$(Split-Path $Exe -Leaf) $($Arguments[0..1] -join ' ')' failed with exit code ${code}:`n$text"
    }
    if ($Capture) { return $stdout.Trim() }   # stdout only: tools such as 'az' print warnings to stderr
    if ($text) { $text -split "`n" | ForEach-Object { Write-Host "    $_" } }
    if ($AllowFailure) { return $true }
}

function Get-Json($text) { if ($text) { return $text | ConvertFrom-Json } }
function SubscriptionOf($resourceId) { if ($resourceId -match '/subscriptions/([^/]+)') { return $Matches[1] } }

function Find-Runtime {
    $candidates = if ($Runtime -eq "auto") { @("docker", "podman") } else { @($Runtime) }
    foreach ($name in $candidates) {
        $cmd = Get-Command $name -ErrorAction SilentlyContinue
        if (-not $cmd -and $name -eq "podman") {
            $fallback = "C:\Program Files\RedHat\Podman\podman.exe"
            if (Test-Path $fallback) { return @{ Name = "podman"; Path = $fallback } }
        }
        if ($cmd) { return @{ Name = $name; Path = $cmd.Source } }
    }
    return $null
}

# Rewrites `param image = '...'` in the Bicep parameter file, but only when the file is for this app and registry.
function Update-ParamFile {
    param([string] $Path, [string] $NewImage, [string] $AppName, [string] $RegistryName, [switch] $WhatIf)
    if (-not (Test-Path $Path)) { return "skipped: $Path does not exist" }
    $text = [System.IO.File]::ReadAllText($Path)
    if ($text -notmatch "(?m)^\s*param\s+appName\s*=\s*'$([regex]::Escape($AppName))'") { return "skipped: the file is not for app '$AppName'" }
    if ($text -notmatch "(?m)^\s*param\s+registryName\s*=\s*'$([regex]::Escape($RegistryName))'") { return "skipped: the file does not use registry '$RegistryName'" }
    $pattern = "(?m)^(\s*param\s+image\s*=\s*')[^']*(')"
    if ($text -notmatch $pattern) { return "skipped: no `param image = '...'` line found" }
    if ($text -match "(?m)^\s*param\s+image\s*=\s*'$([regex]::Escape($NewImage))'") { return "already up to date" }
    if ($WhatIf) { return "would update" }
    $updated = [regex]::Replace($text, $pattern, { param($m) $m.Groups[1].Value + $NewImage + $m.Groups[2].Value }, 1)
    [System.IO.File]::WriteAllText($Path, $updated, (New-Object System.Text.UTF8Encoding $false))
    return "updated"
}

# ================================================================ 1. Preflight
Step "Preflight: Azure sign-in$(if ($Registry) { ", registry '$Registry'" })$(if (-not $NoAppUpdate) { ", app '$AppName'" })"
if (-not (Get-Command az -ErrorAction SilentlyContinue)) { throw "Azure CLI ('az') was not found. Install it from https://aka.ms/installazurecli" }
$me = Get-Json (Invoke-Native az @("account", "show", "--query", "{user:user.name,tenant:tenantId,subscription:name}", "-o", "json") -Capture -ReadOnly -AllowFailure)
if (-not $me) { throw "Not signed in to the Azure CLI. Run 'az login' first." }
Info "signed in as $($me.user)  (default subscription '$($me.subscription)', tenant $($me.tenant))"

# The app is read first, because by default the registry is the one the app already pulls from.
$app = $null
if (-not $NoAppUpdate) {
    $appJson = Invoke-Native az (@("containerapp", "show", "-n", $AppName, "-g", $AppResourceGroup, "-o", "json") + (SubArgs $AppSubscription)) -Capture -ReadOnly -AllowFailure
    if (-not $appJson) { throw "Container App '$AppName' was not found in resource group '$AppResourceGroup'. Check -AppName, -AppResourceGroup and -AppSubscription, and that 'az' is signed in to the tenant the app is in." }
    $app = Get-Json $appJson
    $appSubscription = SubscriptionOf $app.id
    $appTenant = Invoke-Native az @("account", "show", "--subscription", $appSubscription, "--query", "tenantId", "-o", "tsv") -Capture -ReadOnly -AllowFailure
    $appRegistries = @($app.properties.configuration.registries | Where-Object { $_ })
    $currentImage = $app.properties.template.containers[0].image
    $fqdn = $app.properties.configuration.ingress.fqdn
    Info "app:      $($app.name)  ($($app.location), subscription $appSubscription, tenant $appTenant)"
    Info "          revision mode $($app.properties.configuration.activeRevisionsMode), current image $currentImage"
    Info "          pulls from: $((($appRegistries | ForEach-Object { $_.server }) -join ', ') -replace '^$', '(no registry configured)')"
}

if (-not $Registry) {
    if ($NoAppUpdate) { throw "-Registry is required with -NoAppUpdate: there is no app to take the registry from." }
    if ($appRegistries.Count -ne 1) {
        throw "Cannot choose the registry: the app pulls from $($appRegistries.Count) registries. Pass -Registry <name>."
    }
    if ($appRegistries[0].server -notmatch '^([^.]+)\.azurecr\.') { throw "The app's registry '$($appRegistries[0].server)' is not an Azure Container Registry. Pass -Registry <name>." }
    $Registry = $Matches[1]
    Info "registry: '$Registry' (the one the app already pulls from; pass -Registry to use another)"
}

$acrJson = Invoke-Native az (@("acr", "show", "-n", $Registry, "-o", "json") + (SubArgs $RegistrySubscription)) -Capture -ReadOnly -AllowFailure
if (-not $acrJson) {
    $visible = (Invoke-Native az @("account", "list", "--query", "[].name", "-o", "tsv") -Capture -ReadOnly -AllowFailure) -replace "`n", ", "
    throw ("Registry '$Registry' was not found. The Azure CLI session can see these subscriptions: $visible.`n" +
           "If the registry is in another subscription, pass -RegistrySubscription <id>. If it is in another tenant, run " +
           "'az login --tenant <tenant-id>' first.")
}
$acr = Get-Json $acrJson
$server = $acr.loginServer
$acrSubscription = SubscriptionOf $acr.id
$acrTenant = Invoke-Native az @("account", "show", "--subscription", $acrSubscription, "--query", "tenantId", "-o", "tsv") -Capture -ReadOnly -AllowFailure
Info "registry: $server  (subscription $acrSubscription, tenant $acrTenant, SKU $($acr.sku.name))"

$pullMode = "none"; $pullIdentity = $null; $pullPrincipal = $null
if (-not $NoAppUpdate) {
    $userIdentities = @()
    if ($app.identity -and $app.identity.userAssignedIdentities) { $userIdentities = @($app.identity.userAssignedIdentities.PSObject.Properties) }
    $registryEntry = $appRegistries | Where-Object { $_.server -eq $server } | Select-Object -First 1

    if ($registryEntry) {
        $pullMode = "existing"
        $how = if ($registryEntry.identity) { "managed identity $(($registryEntry.identity -split '/')[-1])" } elseif ($registryEntry.username) { "the stored credentials for '$($registryEntry.username)'" } else { "its configured access" }
        Info "pull path: the app already pulls from $server with $how - that is kept."
    }
    elseif ($appTenant -and $acrTenant -and $appTenant -eq $acrTenant) {
        $pullMode = "identity"
        if ($userIdentities.Count -eq 1) {
            $pullIdentity = $userIdentities[0].Name; $pullPrincipal = $userIdentities[0].Value.principalId
            Info "pull path: the app is not configured for $server. It will use its user-assigned managed identity '$(($pullIdentity -split '/')[-1])' with the AcrPull role."
        }
        else {
            $pullIdentity = "system"
            Info "pull path: the app is not configured for $server. It will use its system-assigned managed identity with the AcrPull role."
        }
    }
    else {
        throw ("The Container App '$AppName' cannot pull from '$server':`n" +
               "  - the app is not configured to use that registry, and`n" +
               "  - the app is in tenant $appTenant but the registry is in tenant $acrTenant; a managed identity cannot be granted access across tenants.`n" +
               "Nothing was built or changed. Options:`n" +
               "  1. Publish to a registry the app already uses: ./publish-image.ps1 -Registry <name> (the app pulls from: $((($appRegistries | ForEach-Object { $_.server }) -join ', '))).`n" +
               "  2. Give the app credentials for $server yourself (for example a repository-scoped ACR token), then run this script again:`n" +
               "     az containerapp registry set -n $AppName -g $AppResourceGroup --server $server --username <name> --password <secret>")
    }

    # The app's current image is often a moving tag such as ":latest" that this run is about to overwrite.
    # Resolve it to a digest now, so the rollback command still points at the version that is running today.
    $previousRef = $currentImage
    if ($currentImage -notmatch '@sha256:' -and $currentImage -match '^([^/]+)/([^:@]+):(.+)$' -and $Matches[1] -eq $server) {
        $prevRepo = $Matches[2]; $prevTag = $Matches[3]
        $prevDigest = Invoke-Native az (@("acr", "repository", "show", "-n", $Registry, "--image", "${prevRepo}:$prevTag", "--query", "digest", "-o", "tsv") + (SubArgs $RegistrySubscription)) -Capture -ReadOnly -AllowFailure
        if ($prevDigest) { $previousRef = "$server/${prevRepo}@$prevDigest"; Info "          that tag currently resolves to $prevDigest (kept for rollback)" }
    }
}

# ================================================================ 2. Tag
if (-not $Tag) {
    $sha = "nogit"
    if (Get-Command git -ErrorAction SilentlyContinue) {
        $prev = $ErrorActionPreference; $ErrorActionPreference = "Continue"
        $head = (& git -C $contextDir rev-parse --short=7 HEAD 2>$null)
        $dirty = (& git -C $contextDir status --porcelain -- $contextDir 2>$null)
        $ErrorActionPreference = $prev
        if ($head) { $sha = "$head"; if ($dirty) { $sha += "-dirty" } }
    }
    $Tag = "{0}-{1}" -f $startedUtc.ToString("yyyyMMdd"), $sha
}
if ($Tag -notmatch '^[A-Za-z0-9_][A-Za-z0-9_.-]{0,127}$') { throw "'$Tag' is not a valid image tag." }
$image = "{0}/{1}:{2}" -f $server, $Repository, $Tag
$latest = "{0}/{1}:latest" -f $server, $Repository
Step "Image"
Info "$image$(if (-not $NoLatest) { '  (+ latest)' })"

if ($Tag -ne "latest" -and -not $DryRun) {
    $prev = $ErrorActionPreference; $ErrorActionPreference = "Continue"
    $existing = (& az acr repository show-tags -n $Registry --repository $Repository -o tsv @(SubArgs $RegistrySubscription) 2>$null) -join " "
    $ErrorActionPreference = $prev
    if ($existing -and (($existing -split "\s+") -contains $Tag)) { throw "Tag '$Tag' already exists in '$Repository'. Pass a different -Tag so the earlier image is not overwritten." }
}

# ================================================================ 3. Build and push
$labels = @("org.opencontainers.image.title=csm-learn-catalog",
            "org.opencontainers.image.created=$($startedUtc.ToString('s'))Z")
# A new value every run invalidates the Dockerfile layer that downloads the catalog, so the image
# always contains a fresh catalog instead of one cached from an earlier build.
$refresh = $startedUtc.ToString("yyyyMMddHHmmss")
if ($UseAcrBuild) {
    Step "Building in the registry with ACR Tasks (no local container runtime needed)"
    $buildArgs = @("acr", "build", "-r", $Registry, "-t", "${Repository}:$Tag", "--build-arg", "CATALOG_REFRESH=$refresh")
    if (-not $NoLatest) { $buildArgs += @("-t", "${Repository}:latest") }
    foreach ($l in $labels) { $buildArgs += @("--image-label", $l) }
    $buildArgs += (SubArgs $RegistrySubscription)
    $buildArgs += $contextDir
    Invoke-Native az $buildArgs
}
else {
    $rt = Find-Runtime
    if (-not $rt) { throw "No container runtime found. Install Docker or Podman, or re-run with -UseAcrBuild." }
    Step "Building the image with $($rt.Name)"
    $buildArgs = @("build", "-t", $image, "--build-arg", "CATALOG_REFRESH=$refresh")
    if (-not $NoLatest) { $buildArgs += @("-t", $latest) }
    foreach ($l in $labels) { $buildArgs += @("--label", $l) }
    $buildArgs += $contextDir
    Invoke-Native $rt.Path $buildArgs

    Step "Signing in to $server with an Entra token"
    $token = Invoke-Native az (@("acr", "login", "-n", $Registry, "--expose-token", "--output", "tsv", "--query", "accessToken") + (SubArgs $RegistrySubscription)) -Capture
    if (-not $DryRun -and $token -notmatch '^[\w-]+\.[\w-]+\.[\w-]+$') { throw "Could not get a registry access token from 'az acr login --expose-token'." }
    Invoke-Native $rt.Path @("login", $server, "--username", "00000000-0000-0000-0000-000000000000", "--password-stdin") -StdIn $token

    Step "Pushing"
    Invoke-Native $rt.Path @("push", $image)
    if (-not $NoLatest) { Invoke-Native $rt.Path @("push", $latest) }
}

# ================================================================ 4. Verify the push
Step "Verifying the image in the registry"
$digest = Invoke-Native az (@("acr", "repository", "show", "-n", $Registry, "--image", "${Repository}:$Tag", "--query", "digest", "-o", "tsv") + (SubArgs $RegistrySubscription)) -Capture
if ($DryRun) { $digest = "sha256:<digest>" }
$tags = Invoke-Native az (@("acr", "repository", "show-tags", "-n", $Registry, "--repository", $Repository, "--detail", "--query", "[?digest=='$digest'].name", "-o", "tsv") + (SubArgs $RegistrySubscription)) -Capture
$deployRef = "$server/${Repository}@$digest"
if ($DryRun) {
    Write-Host "`nWould publish (dry run - nothing was built or pushed):" -ForegroundColor Yellow
    Info "image:  $image$(if (-not $NoLatest) { '  (+ latest)' })"
    Info "deploy by digest: $deployRef"
}
else {
    Write-Host "`nPublished." -ForegroundColor Green
    Info "image:  $image"
    Info "digest: $digest"
    Info "tags on this digest: $(($tags -split '\s+' | Where-Object { $_ }) -join ', ')"
    Info "deploy by digest: $deployRef"
}

if ($NoAppUpdate) { if ($DryRun) { Write-Host "`nDry run finished: nothing was built, pushed or changed." -ForegroundColor Yellow }; return }

# ================================================================ 5. Update the Container App
Step "Updating Container App '$AppName'"
$appSub = SubArgs $AppSubscription
$appTarget = @("-n", $AppName, "-g", $AppResourceGroup) + $appSub
$oldRevision = $app.properties.latestRevisionName

if ($pullMode -eq "identity") {
    if ($pullIdentity -eq "system") {
        Info "Setting up pull access with the app's system-assigned managed identity"
        $pullPrincipal = Invoke-Native az (@("containerapp", "identity", "assign", "--system-assigned", "--query", "principalId", "-o", "tsv") + $appTarget) -Capture
    }
    else { Info "Setting up pull access with the app's user-assigned managed identity" }
    $hasRole = Invoke-Native az (@("role", "assignment", "list", "--assignee", $pullPrincipal, "--scope", $acr.id, "--role", "AcrPull", "--query", "[0].id", "-o", "tsv") + (SubArgs $RegistrySubscription)) -Capture -ReadOnly -AllowFailure
    if (-not $hasRole -or $DryRun) {
        Invoke-Native az (@("role", "assignment", "create", "--assignee-object-id", $pullPrincipal, "--assignee-principal-type", "ServicePrincipal", "--role", "AcrPull", "--scope", $acr.id, "-o", "none") + (SubArgs $RegistrySubscription))
    }
    else { Info "AcrPull is already assigned to the identity." }

    # A new role assignment can take a minute or two to take effect, so retry.
    $configured = $false
    foreach ($attempt in 1..8) {
        $ok = Invoke-Native az (@("containerapp", "registry", "set", "--server", $server, "--identity", $pullIdentity, "-o", "none") + $appTarget) -AllowFailure
        if ($DryRun -or $ok) { $configured = $true; break }
        Info "Role assignment is still propagating (attempt $attempt of 8); waiting 20 seconds"
        Start-Sleep -Seconds 20
    }
    if (-not $configured) { throw "Could not configure '$server' on the app. Check that the identity has the AcrPull role, then run the script again." }
}

Info "Switching to $deployRef"
$createdRevision = Invoke-Native az (@("containerapp", "update", "--image", $deployRef, "--query", "properties.latestRevisionName", "-o", "tsv") + $appTarget) -Capture
Info "update accepted; latest revision: $createdRevision"

if ($DryRun) {
    if (-not $NoParamUpdate) { Info "$(Split-Path $ParamFile -Leaf): $(Update-ParamFile -Path $ParamFile -NewImage $deployRef -AppName $AppName -RegistryName $Registry -WhatIf) (image would be set to the new digest)" }
    Write-Host "`nDry run finished: nothing was built, pushed or changed." -ForegroundColor Yellow; return
}

Step "Waiting for the new revision (up to $TimeoutMinutes minutes)"
$deadline = (Get-Date).AddMinutes($TimeoutMinutes)
$healthy = $false; $newRevision = $null; $rev = $null
while ((Get-Date) -lt $deadline) {
    $newRevision = Invoke-Native az (@("containerapp", "show", "--query", "properties.latestRevisionName", "-o", "tsv") + $appTarget) -Capture -ReadOnly
    if ($newRevision -and $newRevision -ne $oldRevision) {
        $rev = Get-Json (Invoke-Native az (@("containerapp", "revision", "show", "--revision", $newRevision, "--query", "{health:properties.healthState,running:properties.runningState,active:properties.active,image:properties.template.containers[0].image,created:properties.createdTime}", "-o", "json") + $appTarget) -Capture -ReadOnly)
        Info "revision $newRevision : health=$($rev.health) running=$($rev.running) active=$($rev.active)"
        if ($rev.health -eq "Healthy" -and $rev.running -like "Running*") { $healthy = $true; break }
        if ($rev.running -eq "Failed" -or $rev.health -eq "Unhealthy") { break }
    }
    Start-Sleep -Seconds 10
}
if (-not $healthy) {
    throw ("The new revision '$newRevision' did not become healthy. In Single revision mode the previous revision '$oldRevision' keeps serving traffic.`n" +
           "Look at the startup logs: az containerapp logs show -n $AppName -g $AppResourceGroup --type system`n" +
           "Roll back or retry: az containerapp update -n $AppName -g $AppResourceGroup --image $previousRef")
}

Step "Checking the running app"
$checked = $false; $meta = $null
if ($fqdn) {
    foreach ($attempt in 1..12) {
        try {
            $health = Invoke-RestMethod "https://$fqdn/health" -TimeoutSec 20
            Info "GET /health -> $($health.status), $($health.records) records"
            try {
                $meta = Invoke-RestMethod "https://$fqdn/meta" -TimeoutSec 20
                $fileModified = [datetimeoffset]::Parse($meta.file_modified).UtcDateTime
                Info "GET /meta   -> catalog downloaded $($meta.file_modified) (this run started $($startedUtc.ToString('s'))Z)"
                if ($fileModified -lt $startedUtc.AddMinutes(-1)) { Write-Warning "The app is serving a catalog older than this run. Check that revision '$newRevision' is the one receiving traffic." }
            }
            catch { Info "GET /meta   -> not available without the API key (only /health was checked)" }
            $checked = $true; break
        }
        catch { Info "waiting for the app to answer (attempt $attempt of 12): $($_.Exception.Message)"; Start-Sleep -Seconds 10 }
    }
    if (-not $checked) { Write-Warning "The revision is healthy but https://$fqdn/health did not answer. Check the ingress settings." }
}
else { Info "The app has no ingress, so only the revision health was checked." }

$paramResult = $null
if (-not $NoParamUpdate) {
    $paramResult = Update-ParamFile -Path $ParamFile -NewImage $deployRef -AppName $AppName -RegistryName $Registry
    Info "$(Split-Path $ParamFile -Leaf): $paramResult"
}

Write-Host "`nDeployed." -ForegroundColor Green
Info "app:       $AppName ($AppResourceGroup)"
Info "revision:  $newRevision (previous: $oldRevision)"
Info "image:     $deployRef"
Info "was:       $currentImage$(if ($previousRef -ne $currentImage) { "  (resolved to $previousRef before this run moved the tag)" })"
if ($fqdn) { Info "url:       https://$fqdn" }
Info "roll back: az containerapp update -n $AppName -g $AppResourceGroup --image $previousRef"
if ($paramResult -eq "updated") { Info "next:      commit $(Split-Path $ParamFile -Leaf) so a later redeploy of the Bicep template keeps this version" }
