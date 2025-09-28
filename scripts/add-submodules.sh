#!/usr/bin/env bash
set -euo pipefail

MAP_PATH=${1:-repo-map.json}

if [[ ! -f "$MAP_PATH" ]]; then
  echo "repo-map.json not found at $MAP_PATH" >&2
  exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "This script requires 'jq'. Please install jq or use the PowerShell script." >&2
  exit 1
fi

count=$(jq '.repositories | length' "$MAP_PATH")
if [[ "$count" == "null" || "$count" -eq 0 ]]; then
  echo "Invalid repo-map.json: missing or empty 'repositories' array" >&2
  exit 1
fi

for i in $(seq 0 $((count-1))); do
  name=$(jq -r ".repositories[$i].name" "$MAP_PATH")
  path=$(jq -r ".repositories[$i].path" "$MAP_PATH")
  branch=$(jq -r ".repositories[$i].branch // \"main\"" "$MAP_PATH")
  url=$(jq -r ".repositories[$i].url" "$MAP_PATH")

  if [[ -z "$url" || "$url" == "null" ]]; then
    echo "Skipping $name: url is empty in repo-map.json" >&2
    continue
  fi

  parent_dir=$(dirname "$path")
  mkdir -p "$parent_dir"

  echo "Adding submodule: $name -> $path (branch: $branch)"
  git submodule add -b "$branch" "$url" "$path"
done

echo "Initializing and updating submodules recursively..."
git submodule update --init --recursive

echo "Done."


