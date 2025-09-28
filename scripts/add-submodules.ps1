Param(
  [string]$MapPath = "repo-map.json"
)

if (!(Test-Path $MapPath)) {
  Write-Error "repo-map.json not found at $MapPath"
  exit 1
}

$json = Get-Content $MapPath -Raw | ConvertFrom-Json
if (-not $json.repositories) {
  Write-Error "Invalid repo-map.json: missing 'repositories' array"
  exit 1
}

foreach ($repo in $json.repositories) {
  $name = $repo.name
  $path = $repo.path
  $branch = if ($repo.branch) { $repo.branch } else { 'main' }
  $url = $repo.url

  if (-not $url) {
    Write-Warning "Skipping ${name}: url is empty in repo-map.json"
    continue
  }

  if (!(Test-Path (Split-Path $path -Parent))) {
    New-Item -ItemType Directory -Force -Path (Split-Path $path -Parent) | Out-Null
  }

  if (Test-Path $path) {
    Write-Host "Path exists for $name at $path. Checking if it's already a submodule..."
  }

  Write-Host "Adding submodule: $name -> $path (branch: $branch)"
  git submodule add -b $branch $url $path
}

Write-Host "Initializing and updating submodules recursively..."
git submodule update --init --recursive

Write-Host "Done."


