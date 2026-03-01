#!/bin/bash
function downloadAndExecute() {
  local url=$1
  local controlHash=$2
  local runAsRoot=$3

  local tempFile
  local fileHash

  if ! command -v wget &>/dev/null; then
    sudo apt install -y wget
  fi
  if ! command -v rhash &>/dev/null; then
    sudo apt install -y rhash
  fi

  tempFile=$(mktemp)
  wget "$url" -qO "$tempFile"
  fileHash=$(rhash --sha512 "$tempFile" | grep -Eo '^\w+')

  if [[ "$fileHash" == "$controlHash" ]]; then
    echo "File hash matches ($url --> $tempFile)! [sha512.$fileHash]"
    echo "Making file executable..."
    chmod +x "$tempFile"

    echo "Executing file..."
    if [[ "$runAsRoot" == "true" ]]; then
      sudo "$tempFile"
    else
      # shellcheck disable=SC1090
      . "$tempFile"
    fi
  else
    echo "Downloaded file is corrupt!"
    echo "File hash ($url --> $tempFile): sha512.$fileHash"
    echo "Control hash: sha512.$controlHash"
    echo "Abort."
    exit 1
  fi

  echo "Removing temp file $tempFile..."
  rm -vf "$tempFile"
}

function installCommandlineBasics() {
  echo "[UBUNTU SETUP] Install basic command line utilities..."
  sudo apt install -y fish plocate rhash curl optipng rar p7zip-full pdftk-java
}

function installSystemUtils() {
  echo "[UBUNTU SETUP] Install basic system utilities..."
  sudo apt install -y keepass2 gparted usb-creator-gtk
}

function installMultimediaUtils() {
  echo "[UBUNTU SETUP] Installing various multi-media codecs and tools..."
  sudo apt install -y ubuntu-restricted-extras
}

function installMsFonts() {
  if ! read -r -n1 -d "" < <(fc-list | grep -oi "Arial.ttf\|Verdana.ttf\|times.ttf"); then
    echo "[UBUNTU SETUP] Installing MS core fonts..."
    echo sudo apt install -y ttf-mscorefonts-installer fonts-crosextra-carlito fonts-crosextra-caladea
    echo sudo fc-cache -fv
  else
    echo "[UBUNTU SETUP] MS Core Fonts are already installed. Nothing to do."
  fi
  if ! read -r -n1 -d "" < <(fc-list | grep -oi "calibri.ttf"); then
    echo "[UBUNTU SETUP] Installing MS proprietary fonts..."
    echo sudo apt install -y cabextract fontforge
    echo downloadAndExecute https://gist.github.com/maxwelleite/10774746/raw/ttf-vista-fonts-installer.sh 5f7156c1f7598eaf65710061bd96d54a5e10843a78c4bd9cbdd18ed850c91401d464fa9ac7b2f1d245f51da1990e049d7b72bbf19a058fcd8951fb98ade830ce true
    # script calls `sudo fc-cache -fv` automatically after installation
  else
    echo "[UBUNTU SETUP] MS proprietary fonts are already installed. Nothing to do."
  fi
}

function installBrave() {
  if ! command -v brave &>/dev/null; then
    sudo snap install brave
  else
    echo "[UBUNTU SETUP] Brave is already installed. Nothing to do."
  fi
}

function installThunderbird() {
  if ! command -v thunderbird &>/dev/null; then
    sudo snap install thunderbird
  else
    echo "[UBUNTU SETUP] Thunderbird is already installed. Nothing to do."
  fi
}

function installSpotify() {
  if ! command -v spotify &>/dev/null; then
    sudo snap install spotify
  else
    echo "[UBUNTU SETUP] Spotify is already installed. Nothing to do."
  fi
}

function installVlc() {
  if ! command -v vlc &>/dev/null; then
    sudo snap install vlc
  else
    echo "[UBUNTU SETUP] VLC Player is already installed. Nothing to do."
  fi
}

function installSignal() {
  if ! command -v signal-desktop &>/dev/null; then
    sudo snap install signal-desktop
  else
    echo "[UBUNTU SETUP] Signal is already installed. Nothing to do."
  fi
}

function installInkscape() {
  if ! command -v inkscape &>/dev/null; then
    sudo snap install inkscape
  else
    echo "[UBUNTU SETUP] Inkscape is already installed. Nothing to do."
  fi
}

function installFlatpak() {
  if ! command -v flatpak &>/dev/null; then
    sudo apt install -y flatpak gnome-software-plugin-flatpak

    flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
  else
    echo "[UBUNTU SETUP] Flatpak is already installed. Nothing to do."
  fi
}

function installProtonUp() {
  installFlatpak

  if [ -z "$(flatpak info 'net.davidotek.pupgui2' 2>/dev/null)" ]; then
    flatpak install flathub net.davidotek.pupgui2
  else
    echo "[UBUNTU SETUP] ProtonUp-Qt is already installed. Nothing to do."
  fi
}

function installSteam() {
  if ! command -v steam &>/dev/null; then
    sudo apt install -y curl gpg

    curl -fsSL https://repo.steampowered.com/steam/archive/stable/steam.gpg | sudo gpg --dearmor -o /usr/share/keyrings/steam.gpg
    echo "Types: deb
URIs: https://repo.steampowered.com/steam/
Suites: stable
Components: steam
Architectures: amd64 i386
Signed-By: /usr/share/keyrings/steam.gpg" | sudo tee /etc/apt/sources.list.d/steam.sources

    sudo dpkg --add-architecture i386
    sudo apt update
    sudo apt install -y steam-launcher
    # we can safely delete this again because the steam-launcher
    # installer creates a /etc/apt/sources.list.d/steam-stable.list file on its own
    sudo rm -vf /etc/apt/sources.list.d/steam.sources
    sudo apt update

    installProtonUp
  else
    echo "[UBUNTU SETUP] Steam is already installed. Nothing to do."
  fi
}

function installVsCode() {
  if ! command -v code &>/dev/null; then
    sudo snap install code --classic
  else
    echo "[UBUNTU SETUP] VSCode is already installed. Nothing to do."
  fi
}

function installVeracrypt() {
  if ! command -v veracrypt &>/dev/null; then
    sudo add-apt-repository ppa:unit193/encryption -y
    sudo apt update
    sudo apt install -y veracrypt
  else
    echo "[UBUNTU SETUP] Veracrypt is already installed. Nothing to do."
  fi
}

function installNodeJs() {
  if ! [ -f ~/.nvm/nvm.sh ]; then
    echo "[UBUNTU SETUP] Downloading and installing Node Version Manager (nvm)..."
    downloadAndExecute https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.4/install.sh a8e082d8d1a9b61a09e5d3e1902d2930e5b1b84a86f9777c7d2eb50ea204c0141f6a97c54a860bc3282e7b000f1c669c755f5e0db7bd6d492072744c302c0a21

    echo "[UBUNTU SETUP] Installing lates LTS version of Node.js..."
    nvm install --lts
    nvm use --lts
  else
    echo "[UBUNTU SETUP] Node Version Manager (nvm) is already installed. Nothing to do."
  fi
}

function installRust() {
  # Snap-specific verification method: snap list --unicode=never | tail -n +2 | grep -o '^package-name'
  if ! command -v rustup &>/dev/null; then
    # Note: The rustup snap is not officially maintained by the Rust Foundation.
    # While it’s a convenient option for general use, some users report it may lag behind
    # the latest rustup releases compared to the official shell script installer.
    #
    # TODO: consider switching to shell script installer!
    sudo snap install rustup --classic

    rustup install stable
    rustup component add rust-analyzer
  else
    echo "[UBUNTU SETUP] Rust is already installed. Nothing to do."
  fi
}

function installGit() {
  if ! command -v git &>/dev/null; then
    echo "[UBUNTU SETUP] Installing Git..."

    sudo apt install -y git fish

    local publicKey="$HOME/.ssh/id_ed25519.pub"

    if ! [ -f "$publicKey" ]; then
      echo "Error: public key file is missing ($publicKey)"
      echo "Abort."
      exit 1
    fi

    echo "Creating .gitconfig for user $USER..."
    git config --global user.name "Lena M."
    git config --global user.email "lena.miyamoto21@gmail.com"
    git config --global user.signingkey "$publicKey"
    git config --global commit.gpgsign true
    git config --global core.editor "code --wait"
    git config --global credential.helper store
    git config --global gpg.format ssh

    cat <<EOF >>~/.gitconfig

### Copied from: https://blog.gitbutler.com/how-git-core-devs-configure-git ###

# clearly makes git better
[column]
	ui = auto
[branch]
	sort = -committerdate
[tag]
	sort = version:refname
[init]
	defaultBranch = main
[diff]
	algorithm = histogram
	colorMoved = plain
	mnemonicPrefix = true
	renames = true
[push]
	default = simple
	autoSetupRemote = true
	followTags = true
[fetch]
	prune = true
	pruneTags = true
	all = true

# why the hell not?
[help]
	autocorrect = prompt
[commit]
	verbose = true
[rerere]
	enabled = true
	autoupdate = true
[core]
	excludesfile = ~/.gitignore
[rebase]
	autoSquash = true
	autoStash = true
	updateRefs = true

# a matter of taste (uncomment if you dare)
[core]
	# fsmonitor = true
	# untrackedCache = true
[merge]
	# (just 'diff3' if git version < 2.3)
	conflictstyle = zdiff3
[pull]
	rebase = true
EOF
  else
    echo "[UBUNTU SETUP] Git is already installed. Nothing to do."
  fi
}

function installDevTools() {
  echo "[UBUNTU SETUP] Installing essential dev-tools..."

  installGit
  installRust
  installNodeJs
  installVsCode

  sudo apt install -y build-essential gdb lldb shfmt
}

function installGnomeShell() {
  echo "[UBUNTU SETUP] Installing gnome-shell and related utilities..."
  sudo apt install -y ubuntu-gnome-desktop gnome-tweaks gnome-shell-extension-manager gnome-browser-connector
}

function configureGnomeSettings() {
  echo "[UBUNTU SETUP] Adjust GNOME user settings for Gedit and Nautilus ..."
  gsettings set org.gnome.nautilus.preferences default-sort-order 'type'
  gsettings set org.gnome.nautilus.preferences executable-text-activation 'ask'

  gsettings set org.gnome.gedit.preferences.editor display-line-numbers true
  gsettings set org.gnome.gedit.preferences.editor highlight-current-line true
  gsettings set org.gnome.gedit.preferences.editor bracket-matching true
  gsettings set org.gnome.gedit.preferences.editor scheme 'oblivion'
  gsettings set org.gnome.gedit.preferences.editor auto-indent true
  gsettings set org.gnome.gedit.preferences.editor insert-spaces true
  gsettings set org.gnome.gedit.preferences.editor tabs-size 'uint32 2'

  #echo "[UBUNTU SETUP] Disabling GNOME default shortcuts that interfere with IntelliJ and VSCode..."
  #gsettings set org.gnome.desktop.wm.keybindings toggle-shaded "[]"
  #gsettings set org.gnome.desktop.wm.keybindings begin-move "[]"
  #gsettings set org.gnome.desktop.wm.keybindings panel-main-menu "[]"

  #gsettings set org.gnome.desktop.wm.keybindings move-to-workspace-right "[]"
  #gsettings set org.gnome.desktop.wm.keybindings move-to-workspace-left "[]"
  #gsettings set org.gnome.desktop.wm.keybindings move-to-workspace-down "['<Super><Shift>Page_Down']"
  #gsettings set org.gnome.desktop.wm.keybindings move-to-workspace-up "['<Super><Shift>Page_Up']"

  #echo "[UBUNTU SETUP] Set mouse acceleration profile to 'flat' to avoid drag and drop issues..."
  #gsettings set org.gnome.desktop.peripherals.mouse accel-profile 'flat'
  #gsettings set org.gnome.desktop.peripherals.mouse speed 'double 1.0'
}

function startUbuntuSetup() {
  if [[ -n "$BASH_VERSION" ]]; then
    echo "[UBUNTU SETUP] Script is running in Bash ($BASH_VERSION)."
  else
    echo "[UBUNTU SETUP] Script is not running in Bash. Abort."
    exit 1
  fi
  if [ "$USERNAME" == "root" ]; then
    echo "[UBUNTU SETUP] This script is not intended to be run as root! Run as local user instead! Abort."
    exit 1
  else
    echo "[UBUNTU SETUP] Running as user '$USERNAME'."
  fi
  if [ "$(lsb_release -si 2>/dev/null)" != "Ubuntu" ]; then
    echo "[UBUNTU SETUP] Your linux distribution $(lsb_release -si 2>/dev/null) is not supported! Abort."
    exit 1
  fi
  if [ "$(lsb_release -sr 2>/dev/null)" != "24.04" ]; then
    echo "[UBUNTU SETUP] Your Ubuntu version is not supported $(lsb_release -sr 2>/dev/null)! Abort."
    exit 1
  else
    echo "[UBUNTU SETUP] Running on $(lsb_release -sd 2>/dev/null)."
  fi

  echo "[UBUNTU SETUP] Updating packages..."
  sudo apt update

  installCommandlineBasics
  installSystemUtils
  installFlatpak
  installMultimediaUtils

  installBrave
  installThunderbird
  installSpotify
  installVlc
  installSignal
  installInkscape

  installSteam
  installVeracrypt

  installDevTools
  installGnomeShell

  installMsFonts

  configureGnomeSettings

  sudo apt update
  sudo apt upgrade -y
  sudo apt autoremove -y

  sudo snap refresh

  echo "[UBUNTU SETUP] Setup complete!"
  exit 0
}

## MAIN ##
startUbuntuSetup
