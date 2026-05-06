#!/bin/bash
IFS=$'\n\t'
set -euo pipefail
shopt -s globstar nullglob

now=$(date +%s)
limit=$((now - 3600 * 3))

function deleteRecentThumbnails() {
  globPattern="$1/**/*"

  for file in $globPattern; do
    [[ -f "$file" ]] || continue

    if (($(stat -c %Y "$file") > limit)); then
      echo "Delete file '$file' [last modified: $(date -d @"$(stat -c %Y "$file")" "+%Y-%m-%d %H:%M:%S")]..."
      #shred -fuzn 0 "$file"
      rm -vf "$file"
    fi
  done
}

function deleteRecentlyUsed() {
  rm -vf ~/.local/share/recently-used.xbel
}

deleteRecentThumbnails ~/.cache/thumbnails/large
deleteRecentThumbnails ~/.cache/thumbnails/normal
deleteRecentThumbnails ~/.cache/thumbnails/fail
deleteRecentlyUsed
