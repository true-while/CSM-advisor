<#
.SYNOPSIS
    Builds the catalog search image and publishes it to an Azure Container Registry.

.DESCRIPTION
    - Signs in to the registry with a short-lived Microsoft Entra token (no admin user, no stored password).
    - Builds the image from catalog/Dockerfile with Docker or Podman (auto-detected), or inside the registry
      with ACR Tasks (-UseAcrBuild, needs no local container runtime).
    - Pushes an immutable tag (<yyyyMMdd>-<git sha>, plus "-dirty" for uncommitted changes) and, unless
      -NoLatest is given, the moving tag "latest". Prints the image digest to deploy by.

    The catalog is downloaded while the image builds, so the image tag also dates the catalog snapshot.
    Run `az login` first. Your account needs the AcrPush role (Owner and Contributor also work) on the registry.

.EXAMPLE
    ./publish-image.ps1
.EXAMPLE
    ./publish-image.ps1 -Tag 1.0.0 -NoLatest
.EXAMPLE
    ./publish-image.ps1 -UseAcrBuild
.EXAMPLE
    ./publish-image.ps1 -DryRun
#>
[CmdletBinding()]
param(
    [string] $Registry = "msftagentacryqjcqtaqoecly",
    [string] $Repository = "csm-learn-catalog",
    [string] $Tag,
    [string] $Subscription,
    [ValidateSet("auto", "docker", "podman")] [string] $Runtime = "auto",
    [switch] $UseAcrBuild,
    [switch] $NoLatest,
    [switch] $DryRun
)

$ErrorActionPreference = "Stop"
$contextDir = Split-Path -Parent $PSScriptRoot

function Step($text) { Write-Host "`n==> $text" -ForegroundColor Cyan }

# Runs a native command, shows its output, and fails on a non-zero exit code.
# (Windows PowerShell 5.1 turns native stderr into errors, so ErrorActionPreference is relaxed here.)
function Invoke-Native {
    param([string] $Exe, [string[]] $Arguments, [switch] $Capture, [string] $StdIn)
    Write-Host ("  > {0} {1}" -f (Split-Path $Exe -Leaf), (($Arguments | ForEach-Object { if ($_ -match "\s") { '"{0}"' -f $_ } else { $_ } }) -join " ")) -ForegroundColor DarkGray
    if ($DryRun -and -not $Capture) { return }
    if ($DryRun) { return "(dry run)" }
    $prev = $ErrorActionPreference; $ErrorActionPreference = "Continue"
    try {
        if ($StdIn) { $out = $StdIn | & $Exe @Arguments 2>&1 } else { $out = & $Exe @Arguments 2>&1 }
        $code = $LASTEXITCODE
    } finally { $ErrorActionPreference = $prev }
    $text = ($out | ForEach-Object { "$_" }) -join "`n"
    $stdout = ($out | Where-Object { $_ -isnot [System.Management.Automation.ErrorRecord] } | ForEach-Object { "$_" }) -join "`n"
    if ($code -ne 0) { throw "'$(Split-Path $Exe -Leaf) $($Arguments[0])' failed with exit code ${code}:`n$text" }
    if ($Capture) { return $stdout.Trim() }   # stdout only: tools such as 'az' print warnings to stderr
    if ($text) { $text -split "`n" | ForEach-Object { Write-Host "    $_" } }
}

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

# ---------------------------------------------------------------- Azure
Step "Checking Azure sign-in and registry '$Registry'"
if (-not (Get-Command az -ErrorAction SilentlyContinue)) { throw "Azure CLI ('az') was not found. Install it from https://aka.ms/installazurecli" }
if ($Subscription) { Invoke-Native az @("account", "set", "--subscription", $Subscription) }
if ($DryRun) { $account = "(dry run)"; $server = "$Registry.azurecr.io" }
else {
    $account = Invoke-Native az @("account", "show", "--query", "[user.name,name]", "-o", "tsv") -Capture
    if (-not $account) { throw "Not signed in. Run 'az login' first." }
    $server = Invoke-Native az @("acr", "show", "-n", $Registry, "--query", "loginServer", "-o", "tsv") -Capture
    if (-not $server) { throw "Registry '$Registry' was not found in the current subscription. Use -Subscription to select the right one." }
}
Write-Host "  signed in as / subscription: $(if ($DryRun) { $account } else { ($account -split '\s+') -join ' / ' })"
Write-Host "  registry login server:       $server"

# ---------------------------------------------------------------- Tag
if (-not $Tag) {
    $sha = "nogit"
    if (Get-Command git -ErrorAction SilentlyContinue) {
        $prev = $ErrorActionPreference; $ErrorActionPreference = "Continue"
        $head = (& git -C $contextDir rev-parse --short=7 HEAD 2>$null)
        $dirty = (& git -C $contextDir status --porcelain -- $contextDir 2>$null)
        $ErrorActionPreference = $prev
        if ($head) { $sha = "$head"; if ($dirty) { $sha += "-dirty" } }
    }
    $Tag = "{0}-{1}" -f (Get-Date).ToUniversalTime().ToString("yyyyMMdd"), $sha
}
if ($Tag -notmatch '^[A-Za-z0-9_][A-Za-z0-9_.-]{0,127}$') { throw "'$Tag' is not a valid image tag." }
$image = "{0}/{1}:{2}" -f $server, $Repository, $Tag
$latest = "{0}/{1}:latest" -f $server, $Repository
Write-Host "  image: $image$(if (-not $NoLatest) { '  (+ latest)' })"

if ($Tag -ne "latest" -and -not $DryRun) {
    $prev = $ErrorActionPreference; $ErrorActionPreference = "Continue"
    $existing = (& az acr repository show-tags -n $Registry --repository $Repository -o tsv 2>$null) -join " "
    $ErrorActionPreference = $prev
    if ($existing -and (($existing -split "\s+") -contains $Tag)) { throw "Tag '$Tag' already exists in '$Repository'. Pass a different -Tag so the earlier image is not overwritten." }
}

# ---------------------------------------------------------------- Build and push
$labels = @("org.opencontainers.image.title=csm-learn-catalog",
            "org.opencontainers.image.created=$((Get-Date).ToUniversalTime().ToString('s'))Z")
# A new value every run invalidates the Dockerfile layer that downloads the catalog, so the image
# always contains a fresh catalog instead of one cached from an earlier build.
$refresh = (Get-Date).ToUniversalTime().ToString("yyyyMMddHHmmss")
if ($UseAcrBuild) {
    Step "Building in the registry with ACR Tasks (no local container runtime needed)"
    $buildArgs = @("acr", "build", "-r", $Registry, "-t", "${Repository}:$Tag", "--build-arg", "CATALOG_REFRESH=$refresh")
    if (-not $NoLatest) { $buildArgs += @("-t", "${Repository}:latest") }
    foreach ($l in $labels) { $buildArgs += @("--image-label", $l) }
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
    $token = Invoke-Native az @("acr", "login", "-n", $Registry, "--expose-token", "--output", "tsv", "--query", "accessToken") -Capture
    if (-not $DryRun -and $token -notmatch '^[\w-]+\.[\w-]+\.[\w-]+$') { throw "Could not get a registry access token from 'az acr login --expose-token'." }
    Invoke-Native $rt.Path @("login", $server, "--username", "00000000-0000-0000-0000-000000000000", "--password-stdin") -StdIn $token

    Step "Pushing"
    Invoke-Native $rt.Path @("push", $image)
    if (-not $NoLatest) { Invoke-Native $rt.Path @("push", $latest) }
}

# ---------------------------------------------------------------- Verify
if ($DryRun) { Write-Host "`nDry run finished: nothing was built or pushed." -ForegroundColor Yellow; return }
Step "Verifying the image in the registry"
$digest = Invoke-Native az @("acr", "repository", "show", "-n", $Registry, "--image", "${Repository}:$Tag", "--query", "digest", "-o", "tsv") -Capture
$tags = Invoke-Native az @("acr", "repository", "show-tags", "-n", $Registry, "--repository", $Repository, "--detail", "--query", "[?digest=='$digest'].name", "-o", "tsv") -Capture
Write-Host "`nPublished." -ForegroundColor Green
Write-Host "  image:  $image"
Write-Host "  digest: $digest"
Write-Host "  tags on this digest: $(($tags -split '\s+' | Where-Object { $_ }) -join ', ')"
Write-Host "  deploy by digest: $server/${Repository}@$digest"
