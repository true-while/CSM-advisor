<#
.SYNOPSIS
    Packages the Learn Path Adviser plugin into dist/learn-path-adviser.zip for Cowork install/update.
#>
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$dist = Join-Path $root "dist"
$zipPath = Join-Path $dist "learn-path-adviser.zip"
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

if (Test-Path $zipPath) { Remove-Item -Force $zipPath }
Compress-Archive -Path (Join-Path $stagingDir "*") -DestinationPath $zipPath
Remove-Item -Recurse -Force $stagingDir

Write-Host "Packaged $zipPath"
