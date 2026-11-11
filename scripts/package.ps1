<#
.SYNOPSIS
    Packages the CSM Advisor plugin into dist/CSM-advisor.zip for Cowork install/update.
#>
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$dist = Join-Path $root "dist"
$zipPath = Join-Path $dist "CSM-advisor.zip"
$stagingDir = Join-Path $dist "staging"

if (Test-Path $stagingDir) { Remove-Item -Recurse -Force $stagingDir }
New-Item -ItemType Directory -Path $stagingDir | Out-Null

$itemsToPackage = @("manifest.json", "color.png", "outline.png", "skills")
foreach ($item in $itemsToPackage) {
    $sourcePath = Join-Path $root $item
    if (-not (Test-Path $sourcePath)) {
        throw "Required item not found: $item"
    }
    Copy-Item -Path $sourcePath -Destination $stagingDir -Recurse
}

# The Learn catalog is generated, not committed. Release builds create it first; warn if it is missing.
$catalog = Join-Path $stagingDir "skills\csm-advisor\ms-learn-catalog.json"
if (-not (Test-Path $catalog)) {
    Write-Warning "ms-learn-catalog.json not found - run 'python scripts/build_learn_catalog.py' first to bundle it."
}

if (Test-Path $zipPath) { Remove-Item -Force $zipPath }
Compress-Archive -Path (Join-Path $stagingDir "*") -DestinationPath $zipPath
Remove-Item -Recurse -Force $stagingDir

Write-Host "Packaged $zipPath"
