#!/bin/bash
IFS=$'\n\t'
set -euo pipefail
shopt -s dotglob nullglob

HOME_DIR="${1:-$HOME}"

printf "\033[1;31mYou're about to delete most of %s - do you whish to proceed?\033[0m\n" "$HOME_DIR"
read -rp "Enter the following phrase to continue: NUKE MY HOME! > " nukePhrase

if [[ "$nukePhrase" != "NUKE MY HOME!" ]]; then
  echo "Incorrect nuke phrase. Abort."
  exit 1
fi

for path in "$HOME_DIR"/*; do
  if [ -d "$path" ]; then
    case "$path" in
    "$HOME_DIR"/.ssh | "$HOME_DIR"/.pki | "$HOME_DIR"/.gnupg | "$HOME_DIR"/.steam | "$HOME_DIR"/.local | "$HOME_DIR"/.config | "$HOME_DIR"/.cache | "$HOME_DIR"/Desktop | "$HOME_DIR"/Documents | "$HOME_DIR"/Downloads | "$HOME_DIR"/Music | "$HOME_DIR"/Pictures | "$HOME_DIR"/Public | "$HOME_DIR"/Templates | "$HOME_DIR"/Videos)
      printf "\e[32m🍀 Preserve dir: %s\n\e[0m" "$path"
      ;;
    *)
      rm -vrf "$path"
      ;;
    esac
  elif [ -f "$path" ]; then
    case $path in
    "$HOME_DIR"/.bash_history | "$HOME_DIR"/.recently-used | "$HOME_DIR"/.steampath | "$HOME_DIR"/.steampid)
      printf "\e[32m🍀 Preserve file: %s\n\e[0m" "$path"
      ;;
    *)
      rm -vf "$path"
      ;;
    esac
  else
    # hard- and softlinks
    echo rm -vf "$path"
  fi
done

for path in "$HOME_DIR"/.local/share/*; do
  if [ -d "$path" ]; then
    case $path in
    "$HOME_DIR"/.local/share/applications | "$HOME_DIR"/.local/share/fish | "$HOME_DIR"/.local/share/keyrings | "$HOME_DIR"/.local/share/Steam)
      printf "\e[32m🍀 Preserve dir: %s\n\e[0m" "$path"
      ;;
    *)
      rm -vrf "$path"
      ;;
    esac
  else
    rm -vf "$path"
  fi
done

for path in "$HOME_DIR"/.config/*; do
  if [ -d "$path" ]; then
    case $path in
    "$HOME_DIR"/.config/Signal | "$HOME_DIR"/.config/KeePass | "$HOME_DIR"/.config/fish | "$HOME_DIR"/.config/BraveSoftware)
      printf "\e[32m🍀 Preserve dir: %s\n\e[0m" "$path"
      ;;
    *)
      rm -vrf "$path"
      ;;
    esac
  else
    rm -vf "$path"
  fi
done

for path in "$HOME_DIR"/.cache/*; do
  if [ -d "$path" ]; then
    case $path in
    "$HOME_DIR"/.cache/BraveSoftware)
      printf "\e[32m🍀 Preserve dir: %s\n\e[0m" "$path"
      ;;
    *)
      rm -vrf "$path"
      ;;
    esac
  else
    rm -vf "$path"
  fi
done
