#!/bin/bash
IFS=$'\n\t'
set -euo pipefail

function downloadAndVerify() {
  local url=${1:-}
  local fileName=${2:-}
  local controlHash=${3:-}
  local useTempFile=${4:-}

  local downloadFile
  local fileHash

  if ! command -v wget &>/dev/null; then
    sudo apt install -y wget
  fi
  if ! command -v rhash &>/dev/null; then
    sudo apt install -y rhash
  fi

  if [[ "$useTempFile" == "true" ]]; then
    downloadFile=$(mktemp --suffix=".$fileName")

    # TODO ensure file cleanup on exit (currently throws an odd error)
    # trap 'rm -f -- "$downloadFile"' EXIT
  else
    downloadFile="$HOME/Downloads/$fileName"
  fi

  if [[ "$useTempFile" != "true" ]] && [ -f "$downloadFile" ]; then
    echo "File '$downloadFile' already exists. Skip download."
  else
    echo "Downloading '$url' to '$downloadFile'..."
    wget "$url" -qO "$downloadFile"
  fi

  fileHash=$(rhash --sha512 "$downloadFile" | grep -oE '^\w+')

  if [[ "$fileHash" == "$controlHash" ]]; then
    echo "File hash matches ($url --> $downloadFile)! [sha512.$fileHash]"
    UBUNTU_SETUP_LAST_DOWNLOADED_FILE=$downloadFile
  else
    echo "Downloaded file is corrupt!"
    echo "File hash ($url --> $downloadFile): sha512.$fileHash"
    echo "Control hash: sha512.$controlHash"
    echo "Abort."
    exit 1
  fi
}

function downloadAndExecute() {
  local url=${1:-}
  local fileName=${2:-}
  local controlHash=${3:-}
  local runAsRoot=${4:-}
  local pipeCommands=${5:-}

  downloadAndVerify "$url" "$fileName" "$controlHash" true
  local tempFile=${UBUNTU_SETUP_LAST_DOWNLOADED_FILE:-}

  echo "Making file executable..."
  chmod +x "$tempFile"

  if [[ "$runAsRoot" == "true" ]]; then
    echo "Executing file '$tempFile' as root..."

    if [[ "$pipeCommands" == "" ]]; then
      sudo "$tempFile"
    else
      echo "$pipeCommands" | sudo "$tempFile"
    fi
  else
    echo "Executing file '$tempFile'..."

    if [[ "$pipeCommands" == "" ]]; then
      bash "$tempFile"
    else
      bash -c "echo \"$pipeCommands\" | \"$tempFile\""
    fi
  fi
}

function appendUniqueLineToBashrc() {
  local line=${1:-}
  local bashrc="$HOME/.bashrc"

  touch "$bashrc"
  if ! grep -Fqx "$line" "$bashrc"; then
    printf '%s\n' "$line" >>"$bashrc"
  fi
}

function setGsettingIfSchemaExists() {
  local schema=${1:-}
  local key=${2:-}
  local value=${3:-}

  if gsettings list-schemas | grep -Fxq "$schema"; then
    gsettings set "$schema" "$key" "$value"
  else
    echo "[UBUNTU SETUP] Skip missing gsettings schema: $schema"
  fi
}

function configureFirewall() {
  echo "[UBUNTU SETUP] Setting up UFW (Uncomplicated Firewall)..."
  # ensure firewall is active and enabled on system startup
  sudo ufw enable
  # block common HTTP(S) ports used by local webservers
  sudo ufw deny 8080
  sudo ufw deny 3000
  # block default port for Ollama
  sudo ufw deny 11434

  # list current UFW configuration
  sudo ufw status numbered
}

function configureGnomeSettings() {
  if ! command -v gsettings &>/dev/null; then
    echo "[UBUNTU SETUP] Unexpected error: gsettings is not present!"
    echo "[UBUNTU SETUP] Abort."
    exit 1
  fi

  echo "[UBUNTU SETUP] Adjust GNOME user settings for Nautilus..."
  setGsettingIfSchemaExists org.gnome.nautilus.preferences default-sort-order 'type'
  setGsettingIfSchemaExists org.gnome.nautilus.preferences show-create-link true

  echo "[UBUNTU SETUP] Adjust GNOME user settings for Gedit..."
  setGsettingIfSchemaExists org.gnome.gedit.preferences.editor display-line-numbers true
  setGsettingIfSchemaExists org.gnome.gedit.preferences.editor highlight-current-line true
  setGsettingIfSchemaExists org.gnome.gedit.preferences.editor bracket-matching true
  setGsettingIfSchemaExists org.gnome.gedit.preferences.editor scheme 'oblivion'
  setGsettingIfSchemaExists org.gnome.gedit.preferences.editor auto-indent true
  setGsettingIfSchemaExists org.gnome.gedit.preferences.editor insert-spaces true
  setGsettingIfSchemaExists org.gnome.gedit.preferences.editor tabs-size 'uint32 2'

  echo "[UBUNTU SETUP] Adjust GNOME user settings to disable new annoying tiling feature..."
  setGsettingIfSchemaExists org.gnome.mutter.keybindings toggle-tiled-left "['<Super>Left']"
  setGsettingIfSchemaExists org.gnome.mutter.keybindings toggle-tiled-right "['<Super>Right']"

  #echo "[UBUNTU SETUP] Adjust GNOME user settings to disable default shortcuts that interfere with IntelliJ..."
  #setGsettingIfSchemaExists org.gnome.desktop.wm.keybindings toggle-shaded "['disabled']"

  if [[ "${UBUNTU_SETUP_LENAS_SETUP:-}" == "1" ]] || [[ "${UBUNTU_SETUP_CONFIGURE_LENAS_GSETTINGS:-}" == "1" ]]; then
    echo "[UBUNTU SETUP] Adjust GNOME user settings to disable default shortcuts that interfere with Tomb Raider games..."
    setGsettingIfSchemaExists org.gnome.desktop.wm.keybindings move-to-workspace-down "['<Control><Shift>Down']"
    setGsettingIfSchemaExists org.gnome.desktop.wm.keybindings move-to-workspace-left "['<Control><Shift>Left']"
    setGsettingIfSchemaExists org.gnome.desktop.wm.keybindings move-to-workspace-right "['<Control><Shift>Right']"
    setGsettingIfSchemaExists org.gnome.desktop.wm.keybindings move-to-workspace-up "['<Control><Shift>Up']"

    setGsettingIfSchemaExists org.gnome.desktop.wm.keybindings switch-to-workspace-down "['<Alt><Shift>Down']"
    setGsettingIfSchemaExists org.gnome.desktop.wm.keybindings switch-to-workspace-left "['<Alt><Shift>Left']"
    setGsettingIfSchemaExists org.gnome.desktop.wm.keybindings switch-to-workspace-right "['<Alt><Shift>Right']"
    setGsettingIfSchemaExists org.gnome.desktop.wm.keybindings switch-to-workspace-up "['<Alt><Shift>Up']"

    #echo "[UBUNTU SETUP] Set mouse acceleration profile to 'flat' to avoid drag and drop issues..."
    #setGsettingIfSchemaExists set org.gnome.desktop.peripherals.mouse accel-profile 'flat'
    #setGsettingIfSchemaExists set org.gnome.desktop.peripherals.mouse speed 'double 1.0'
  fi
}

function reconfigureGit() {
  if ! [ -f /usr/share/doc/git/contrib/credential/libsecret/git-credential-libsecret ]; then
    sudo apt install -y make gcc libsecret-1-0 libsecret-1-dev libglib2.0-dev
    sudo make -C /usr/share/doc/git/contrib/credential/libsecret

    if ! [ -f /usr/share/doc/git/contrib/credential/libsecret/git-credential-libsecret ]; then
      echo "Unexpected error: failed to build git-credential-libsecret!"
      echo "Abort."
      exit 1
    fi
  fi

  if [ -f ~/.gitconfig ]; then
    echo "Local git config file ~/.gitconfig already exists. Save existing config as backup in ~/.gitconfig.bak."

    if [ -f ~/.gitconfig.bak ]; then
      echo "Old backup file ~/.gitconfig.bak already exists. Moving ~/.gitconfig.bak to trash..."
      gio trash -f ~/.gitconfig.bak
    fi
    mv ~/.gitconfig ~/.gitconfig.bak
  fi

  if [[ "${UBUNTU_SETUP_LENAS_SETUP:-}" == "1" ]] || [[ "${UBUNTU_SETUP_RECONFIGURE_LENAS_GIT:-}" == "1" ]]; then
    local publicKey="$HOME/.ssh/id_ed25519.pub"

    if ! [ -f "$publicKey" ]; then
      echo "Error: public key file is missing ($publicKey)"
      echo "Abort."
      exit 1
    fi

    echo "Creating .gitconfig for Lena <3..."
    git config --global user.name "Lena M."
    git config --global user.email "lena.miyamoto21@gmail.com"
    git config --global user.signingkey "$publicKey"
    git config --global commit.gpgsign true
    git config --global gpg.format ssh
  else
    echo "Creating .gitconfig for user ${UBUNTU_SETUP_USERNAME:-}..."
    git config --global user.name "${UBUNTU_SETUP_USERNAME:-}"
    git config --global user.email "${UBUNTU_SETUP_USERNAME:-}@mail.com"
  fi

  git config --global core.editor "code --wait"
  git config --global core.autocrlf input
  git config --global credential.helper /usr/share/doc/git/contrib/credential/libsecret/git-credential-libsecret

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
}

function reconfigureVsCode() {
  local node_24

  if [ -d ~/.vscode ]; then
    echo "Moving ~/.vscode to trash ..."
    gio trash -f ~/.vscode
  fi
  if [ -d ~/.config/Code ]; then
    echo "Moving ~/.config/Code to trash ..."
    gio trash -f ~/.config/Code
  fi

  mkdir -p ~/.config/Code/User

  if ! command -v shfmt &>/dev/null; then
    sudo apt install -y shfmt
  fi
  if ! command -v jq &>/dev/null; then
    sudo apt install -y jq
  fi
  if ! command -v fnm &>/dev/null || ! command -v node &>/dev/null; then
    installNodeJs
  fi

  fnm use 24
  node_24="$FNM_DIR/node-versions/$(fnm current)/installation/bin/node"
  if ! [ -x "$node_24" ]; then
    echo "Unexpected error: could not detect Node.js 24 executable!"
    echo "Abort."
    exit 1
  fi

  echo "Installing commonly used VSCode extensions..."
  code --install-extension vscode-icons-team.vscode-icons
  code --install-extension ms-vsliveshare.vsliveshare
  code --install-extension editorconfig.editorconfig
  code --install-extension sanaajani.taskrunnercode
  code --install-extension eamodio.gitlens

  if [[ "${UBUNTU_SETUP_LENAS_SETUP:-}" == "1" ]] || [[ "${UBUNTU_SETUP_RECONFIGURE_LENAS_VSCODE:-}" == "1" ]]; then
    echo "Installing Lena's VSCode extensions <3..."
    code --install-extension vitest.explorer
    code --install-extension ms-playwright.playwright
    code --install-extension esbenp.prettier-vscode
    code --install-extension dbaeumer.vscode-eslint
    code --install-extension rust-lang.rust-analyzer
    code --install-extension mads-hartmann.bash-ide-vscode
    code --install-extension timonwong.shellcheck
    code --install-extension mkhl.shfmt
    code --install-extension dohe.godot-format
    code --install-extension geequlim.godot-tools

    echo "Installing VSCode themes for Lena <3..."
    code --install-extension atomiks.moonlight

    echo "Configuring user settings for Lena's VSCode <3..."
    echo '{}' |
      jq '."editor.tabSize" = 2' |
      jq '."editor.formatOnSave" = false' |
      jq '."editor.defaultFormatter" = "EditorConfig.EditorConfig"' |
      jq '."editor.autoIndentOnPaste" = true' |
      jq '."editor.snippetSuggestions" = "none"' |
      jq '."editor.inlineSuggest.enabled" = false' |
      jq '."editor.bracketPairColorization.independentColorPoolPerBracketType" = true' |
      jq '."editor.fontFamily" = "'\''SeriousShanns Nerd Font Mono'\'', '\''Droid Sans Mono'\'', monospace"' |
      jq '."github.copilot.nextEditSuggestions.enabled" = false' |
      jq '."terminal.integrated.defaultProfile.linux" = "fish"' |
      jq '."typescript.tsserver.nodePath" = "'"$node_24"'"' |
      jq '."typescript.tsserver.maxTsServerMemory" = 10240' |
      jq '."vsicons.dontShowNewVersionMessage" = true' |
      jq '."window.zoomLevel" = 1.4' |
      jq '."workbench.colorTheme" = "Moonlight II"' |
      jq '."workbench.iconTheme" = "vscode-icons"' |
      jq '."workbench.localHistory.maxFileEntries" = 25' |
      jq '."workbench.localHistory.maxFileSize" = 512' \
        >~/.config/Code/User/settings.json

    installCustomFonts
  else
    echo "Configuring basic user settings for VSCode..."
    echo '{}' |
      jq '."editor.tabSize" = 2' |
      jq '."editor.formatOnSave" = false' |
      jq '."editor.defaultFormatter" = "EditorConfig.EditorConfig"' |
      jq '."editor.autoIndentOnPaste" = true' |
      jq '."editor.snippetSuggestions" = "none"' |
      jq '."editor.inlineSuggest.enabled" = false' |
      jq '."editor.bracketPairColorization.independentColorPoolPerBracketType" = true' |
      jq '."github.copilot.nextEditSuggestions.enabled" = false' |
      jq '."terminal.integrated.defaultProfile.linux" = "fish"' |
      jq '."typescript.tsserver.nodePath" = "'"$node_24"'"' |
      jq '."vsicons.dontShowNewVersionMessage" = true' |
      jq '."window.zoomLevel" = 1' |
      jq '."workbench.iconTheme" = "vscode-icons"' \
        >~/.config/Code/User/settings.json
  fi
}

function installCommandlineBasics() {
  echo "[UBUNTU SETUP] Install basic command line utilities..."
  sudo apt install -y fish curl net-tools plocate rhash pwgen p7zip-full rar optipng pdftk-java libsecret-tools mesa-utils apt-transport-https texlive-extra-utils texlive-latex-recommended
}

function installSystemUtils() {
  echo "[UBUNTU SETUP] Install basic system utilities..."
  if [[ "${UBUNTU_SETUP_LENAS_SETUP:-}" == "1" ]]; then
    sudo apt install -y keepass2
  fi
  sudo apt install -y gparted usb-creator-gtk
}

function installMultimediaUtils() {
  echo "[UBUNTU SETUP] Installing various multi-media codecs and tools..."
  sudo apt install -y ubuntu-restricted-extras
}

function installMsFonts() {
  if ! read -r -n1 -d "" < <(fc-list | grep -oi "Arial.ttf\|Verdana.ttf\|times.ttf"); then
    echo "[UBUNTU SETUP] Installing MS core fonts..."
    # automatically accepts the Microsoft End User License Agreement (EULA),
    # preventing the interactive prompt from the ttf-mscorefonts-installer
    echo ttf-mscorefonts-installer msttcorefonts/accepted-mscorefonts-eula select true | sudo debconf-set-selections
    sudo apt install -y ttf-mscorefonts-installer fonts-crosextra-carlito fonts-crosextra-caladea
    sudo fc-cache -fv
  else
    echo "[UBUNTU SETUP] MS Core Fonts are already installed. Nothing to do."
  fi

  if ! read -r -n1 -d "" < <(fc-list | grep -oi "calibri.ttf"); then
    echo "[UBUNTU SETUP] Installing MS proprietary fonts..."
    sudo apt install -y cabextract fontforge
    downloadAndExecute https://gist.github.com/maxwelleite/10774746/raw/ttf-vista-fonts-installer.sh ttf-vista-fonts-installer.sh 5f7156c1f7598eaf65710061bd96d54a5e10843a78c4bd9cbdd18ed850c91401d464fa9ac7b2f1d245f51da1990e049d7b72bbf19a058fcd8951fb98ade830ce true
    # script calls `sudo fc-cache -fv` automatically after installation
  else
    echo "[UBUNTU SETUP] MS proprietary fonts are already installed. Nothing to do."
  fi
}

function installCustomFont() {
  local fontName=${1:-}
  local fontType=${2:-}
  local fontDirectoryName=${3:-}
  local url=${4:-}
  local fileName=${5:-}
  local controlHash=${6:-}

  local fontDirectory="/usr/share/fonts/$fontType/$fontDirectoryName"

  if ! [ -d "$fontDirectory" ]; then
    local fontSuffix

    if [[ "$fontType" == "opentype" ]]; then
      fontSuffix="*.otf"
    elif [[ "$fontType" == "truetype" ]]; then
      fontSuffix="*.ttf"
    else
      echo "Invalid font type: $fontType"
      exit 1
    fi

    echo "[UBUNTU SETUP] Downloading and installing $fontType font '$fontName'..."
    downloadAndVerify "$url" "$fileName" "$controlHash"
    sudo mkdir "$fontDirectory"
    sudo unzip -d "$fontDirectory" -j "${UBUNTU_SETUP_LAST_DOWNLOADED_FILE:-}" "$fontSuffix"

    UBUNTU_SETUP_CUSTOM_FONT_INSTALLED=1
  else
    echo "[UBUNTU SETUP] Font '$fontName' is already installed. Skip."
  fi
}

function installCustomFonts() {
  echo "[UBUNTU SETUP] Installing custom fonts..."

  installCustomFont \
    'Serious Shanns' \
    'opentype' \
    'serious-shanns' \
    'https://github.com/kaBeech/serious-shanns/releases/download/v6.0.0/SeriousShanns.zip' \
    'SeriousShanns.zip' \
    'e45bf5d84894b413bbbbdbcb96359321af6e081dc0cbb27272cbaa85114fb191f24f5bd8d12eb6f1c379d9384e9cd83d3b6c93a937bf4774e46543db2798c687'
  installCustomFont \
    'Montserrat' \
    'opentype' \
    'montserrat' \
    'https://www.1001fonts.com/download/montserrat.zip' \
    'montserrat.zip' \
    'ae0a63dbf2fe11f1321c1c906307cfa7ea3e3248dc510b5cb6edcaf43899b26b0e0488a87c24fc9e9b64d8bce89740560df751cc7ee6273070b2199ab8248a35'
  installCustomFont \
    'Peppy Pegasus' \
    'opentype' \
    'peppy-pegasus' \
    'https://font.download/dl/font/peppy-pegasus.zip' \
    'peppy-pegasus.zip' \
    'c4f547665c1a60956ad07c343d6b923c4ed3287b93b08de083d75ce21d3c2fa2c1e7fb49268f1f2ece2e3d5811622d115ef31cb1777ffb3aad2194587093e9f8'
  installCustomFont \
    'Magic Unicorn' \
    'truetype' \
    'magic-unicorn' \
    'https://dl.dafont.com/dl/?f=magic_unicorn' \
    'magic_unicorn.zip' \
    '75b5e780f07c1df881eb13b0bb58654e1ddbeb5978d9e954eeab6a7da0028ec43e84a73366f8241d71bb93330a7bfdfd2dd09a8619a4f75d0c7757fdb043bfc7'
  installCustomFont \
    'Magic Stary' \
    'opentype' \
    'magic-stary' \
    'https://dl.dafont.com/dl/?f=magic_stary' \
    'magic_stary.zip' \
    '456e4c750ba8736dcd53597eed965ac9c24c5d8db34503fb698fca1a90594da993ace44a0fb8ac7a79c5f562faf1394370e8242db452b44810c767f6c6aa9433'
  installCustomFont \
    'Bad Grunge' \
    'truetype' \
    'bad-grunge' \
    'https://dl.dafont.com/dl/?f=bad_grunge' \
    'bad-grunge.zip' \
    '23de0f49901853029f14350e362baef5e8ee600c87d406c1192421cc53dcb38349783c69f73e24de2cd2cee23690d33c4336a9f3c499cbcce85da437a21e5f9e'
  installCustomFont \
    'Gunplay' \
    'opentype' \
    'gunplay' \
    'https://dl.dafont.com/dl/?f=gunplay' \
    'gunplay.zip' \
    'db512819efc53586b0cd66bd8ecf7aa9fadccf5be41b5901e50eb6b6704a368aa6f1e07787bade6dc08610667f11c3f5503740b3327a04592ac685c65ffc8a24'

  if [[ "${UBUNTU_SETUP_CUSTOM_FONT_INSTALLED:-}" == "1" ]]; then
    sudo fc-cache -fv
  fi
}

function installThunderbird() {
  if ! command -v thunderbird &>/dev/null; then
    echo "[UBUNTU SETUP] Installing Thunderbird..."
    sudo snap install thunderbird
  else
    echo "[UBUNTU SETUP] Thunderbird is already installed. Nothing to do."
  fi
}

function installDiscord() {
  if ! command -v discord &>/dev/null; then
    echo "[UBUNTU SETUP] Installing Discord..."
    sudo snap install discord
  else
    echo "[UBUNTU SETUP] Discord is already installed. Nothing to do."
  fi
}

function installSpotify() {
  if ! command -v spotify &>/dev/null; then
    echo "[UBUNTU SETUP] Installing Spotify..."
    sudo snap install spotify
  else
    echo "[UBUNTU SETUP] Spotify is already installed. Nothing to do."
  fi
}

function installVsCode() {
  if ! command -v code &>/dev/null; then
    echo "[UBUNTU SETUP] Installing VSCode..."
    # update your package list and install required packages
    sudo apt install -y curl gpg
    # download and install the Microsoft GPG key
    curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | sudo gpg --dearmor -o /usr/share/keyrings/microsoft.gpg
    # create the repository configuration file
    echo "Types: deb
URIs: https://packages.microsoft.com/repos/code
Suites: stable
Components: main
Architectures: amd64,arm64,armhf
Signed-By: /usr/share/keyrings/microsoft.gpg
" | sudo tee /etc/apt/sources.list.d/vscode.sources
    # update the package cache and install VS Code
    sudo apt update
    sudo apt install -y code

    reconfigureVsCode
  else
    echo "[UBUNTU SETUP] VSCode is already installed. Nothing to do."
  fi

  if [[ "${UBUNTU_SETUP_INSTALL_OLLAMA:-}" == "1" ]]; then
    # install useful CLI tools for Copilot
    sudo apt install -y jq fdclone bat git-delta shellcheck hyperfine entr tree ripgrep

    echo "[UBUNTU SETUP] Installing OpenCode extension for VSCode..."
    code --install-extension sst-dev.opencode
  fi
}

function installFlatpak() {
  local disableSkipMessage=${1:-}

  if ! command -v flatpak &>/dev/null; then
    echo "[UBUNTU SETUP] Installing Flatpak..."
    sudo apt install -y flatpak gnome-software-plugin-flatpak

    sudo flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
    flatpak remote-add --user --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo

    flatpak update -y --noninteractive
    flatpak update -y --noninteractive --appstream
  elif [[ "$disableSkipMessage" != "true" ]]; then
    echo "[UBUNTU SETUP] Flatpak is already installed. Nothing to do."
  fi
}

function installVlc() {
  if ! command -v vlc &>/dev/null; then
    echo "[UBUNTU SETUP] Installing VLC Player..."
    installFlatpak true

    if ! flatpak info org.videolan.VLC &>/dev/null; then
      flatpak install -y --user flathub org.videolan.VLC
      flatpak run --user org.videolan.VLC &
      disown
    else
      echo "[UBUNTU SETUP] VLC Player is already installed via Flatpak. Nothing to do."
    fi
  else
    echo "[UBUNTU SETUP] VLC Player is already installed. Nothing to do."
  fi
}

function installElement() {
  if ! command -v element-desktop &>/dev/null; then
    echo "[UBUNTU SETUP] Installing Element..."
    installFlatpak true

    if ! flatpak info im.riot.Riot &>/dev/null; then
      flatpak install -y --user flathub im.riot.Riot
      flatpak run --user flathub im.riot.Riot &
      disown

      # The Flatpak version requires specific permissions for file access. By default, it may not access your files.
      # To allow access to common directories like Pictures, Videos, and Documents, use:
      # flatpak override --filesystem=xdg-pictures --filesystem=xdg-videos --filesystem=xdg-documents im.riot.Riot
    else
      echo "[UBUNTU SETUP] Element is already installed via Flatpak. Nothing to do."
    fi
  else
    echo "[UBUNTU SETUP] Element is already installed. Nothing to do."
  fi
}

function installInkscape() {
  if ! command -v inkscape &>/dev/null; then
    echo "[UBUNTU SETUP] Installing Inkscape..."
    installFlatpak true

    if ! flatpak info org.inkscape.Inkscape &>/dev/null; then
      flatpak install -y --user flathub org.inkscape.Inkscape
      flatpak run --user org.inkscape.Inkscape &
      disown
    else
      echo "[UBUNTU SETUP] Inkscape is already installed via Flatpak. Nothing to do."
    fi
  else
    echo "[UBUNTU SETUP] Inkscape is already installed. Nothing to do."
  fi
}

function installGimp() {
  if ! command -v gimp &>/dev/null; then
    echo "[UBUNTU SETUP] Installing Gimp..."
    installFlatpak true

    if ! flatpak info org.gimp.GIMP &>/dev/null; then
      flatpak install -y --user https://flathub.org/repo/appstream/org.gimp.GIMP.flatpakref
      flatpak run --user org.gimp.GIMP &
      disown
    else
      echo "[UBUNTU SETUP] Gimp is already installed via Flatpak. Nothing to do."
    fi
  else
    echo "[UBUNTU SETUP] Gimp is already installed. Nothing to do."
  fi
}

function installBlender() {
  if ! command -v blender &>/dev/null; then
    echo "[UBUNTU SETUP] Installing Blender..."
    installFlatpak true

    if ! flatpak info org.blender.Blender &>/dev/null; then
      flatpak install -y --user flathub org.blender.Blender
      flatpak run --user org.blender.Blender &
      disown
    else
      echo "[UBUNTU SETUP] Blender is already installed via Flatpak. Nothing to do."
    fi
  else
    echo "[UBUNTU SETUP] Blender is already installed. Nothing to do."
  fi
}

function installProtonUp() {
  installFlatpak true

  if ! flatpak info net.davidotek.pupgui2 &>/dev/null; then
    echo "[UBUNTU SETUP] Installing ProtonUp-Qt..."
    flatpak install -y --user flathub net.davidotek.pupgui2
    flatpak run --user net.davidotek.pupgui2 &
    disown
  else
    echo "[UBUNTU SETUP] ProtonUp-Qt is already installed. Nothing to do."
  fi
}

function installMupen64Plus() {
  installFlatpak true

  if ! flatpak info net.sourceforge.m64py.M64Py &>/dev/null; then
    echo "[UBUNTU SETUP] Installing Mupen64Plus + M64Py..."
    flatpak install -y --user flathub net.sourceforge.m64py.M64Py
    flatpak run --user net.sourceforge.m64py.M64Py &
    disown
  else
    echo "[UBUNTU SETUP] Mupen64Plus + M64Py are already installed. Nothing to do."
  fi
}

function installAzahar() {
  installFlatpak true

  if ! flatpak info org.azahar_emu.Azahar &>/dev/null; then
    echo "[UBUNTU SETUP] Installing Azahar..."
    flatpak install -y --user flathub org.azahar_emu.Azahar
    flatpak run --user org.azahar_emu.Azahar &
    disown
  else
    echo "[UBUNTU SETUP] Azahar is already installed. Nothing to do."
  fi
}

function installTorBrowser() {
  if ! command -v torbrowser-launcher &>/dev/null; then
    echo "[UBUNTU SETUP] Installing Tor Browser..."
    sudo apt install -y torbrowser-launcher
  else
    echo "[UBUNTU SETUP] Tor Browser is already installed. Nothing to do."
  fi
}

function installBrave() {
  if ! command -v brave &>/dev/null; then
    echo "[UBUNTU SETUP] Installing Brave..."
    sudo apt install -y curl

    sudo curl -fsSLo /usr/share/keyrings/brave-browser-archive-keyring.gpg https://brave-browser-apt-release.s3.brave.com/brave-browser-archive-keyring.gpg
    sudo curl -fsSLo /etc/apt/sources.list.d/brave-browser-release.sources https://brave-browser-apt-release.s3.brave.com/brave-browser.sources
    sudo apt update
    sudo apt install -y brave-browser
  else
    echo "[UBUNTU SETUP] Brave is already installed. Nothing to do."
  fi
}

function installSignal() {
  if ! command -v signal-desktop &>/dev/null; then
    echo "[UBUNTU SETUP] Installing Signal..."

    # install official public software signing key
    curl -fsSL https://updates.signal.org/desktop/apt/keys.asc | gpg --dearmor >"signal-desktop-keyring.gpg"
    sudo install -m 0644 "signal-desktop-keyring.gpg" /usr/share/keyrings/signal-desktop-keyring.gpg

    # add repository to our list of repositories
    curl -fsSL https://updates.signal.org/static/desktop/apt/signal-desktop.sources -o "signal-desktop.sources"
    sudo install -m 0644 "signal-desktop.sources" /etc/apt/sources.list.d/signal-desktop.sources

    sudo apt update
    sudo apt install -y signal-desktop
  else
    echo "[UBUNTU SETUP] Signal is already installed. Nothing to do."
  fi
}

function installSteam() {
  if ! command -v steam &>/dev/null; then
    echo "[UBUNTU SETUP] Installing Steam..."
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

    if ! [ -d ~/.local/share/Steam ]; then
      mkdir -p ~/.local/share/Steam
    fi
    if ! [ -f ~/.local/share/Steam/steam_dev.cfg ] || ! grep -qE '^@ShaderBackgroundProcessingThreads[[:space:]]+[[:digit:]]+' ~/.local/share/Steam/steam_dev.cfg; then
      echo "@ShaderBackgroundProcessingThreads $(nproc)" >>~/.local/share/Steam/steam_dev.cfg
    fi

    installProtonUp
  else
    echo "[UBUNTU SETUP] Steam is already installed. Nothing to do."
  fi
}

function installJava() {
  if ! command -v javac &>/dev/null; then
    echo "[UBUNTU SETUP] Installing Java..."
    sudo apt install -y openjdk-17-jdk

    echo "Adding JAVA_HOME to ~/.bashrc..."
    export JAVA_HOME
    JAVA_HOME=$(readlink -f /usr/bin/javac | sed 's:/bin/javac::')
    # shellcheck disable=SC2016
    appendUniqueLineToBashrc 'export JAVA_HOME=$(readlink -f /usr/bin/javac | sed "s:/bin/javac::")'
  else
    echo "[UBUNTU SETUP] Java is already installed. Nothing to do."
  fi
}

function installGradle() {
  if ! command -v gradle &>/dev/null; then
    echo "[UBUNTU SETUP] Installing Gradle..."
    sudo apt install -y gradle

    echo "Adding GRADLE_HOME to ~/.bashrc..."
    export GRADLE_HOME
    GRADLE_HOME=$(readlink -f /usr/bin/gradle | sed 's:/bin/gradle::')
    # shellcheck disable=SC2016
    appendUniqueLineToBashrc 'export GRADLE_HOME=$(readlink -f /usr/bin/gradle | sed "s:/bin/gradle::")'
  else
    echo "[UBUNTU SETUP] Gradle is already installed. Nothing to do."
  fi
}

function installAndroidSdk() {
  if ! command -v sdkmanager &>/dev/null; then
    echo "[UBUNTU SETUP] Installing Android SDK..."
    installJava
    installGradle

    echo "[UBUNTU SETUP] Downloading and installing cmdline-tools (Android SDK)..."
    downloadAndVerify "https://dl.google.com/android/repository/commandlinetools-linux-14742923_latest.zip" "commandlinetools-linux-14742923_latest.zip" "b65e830d7655fb39cc9eee669806977f462c49375807ef2c6487fabcc9afdbc210465ce6a1e2429ff95c74ca519d1239daf9a403c30b8d0bdb7a0962af656c8e"
    mkdir -p ~/.local/android/sdk/.temp
    unzip "${UBUNTU_SETUP_LAST_DOWNLOADED_FILE:-}" -d ~/.local/android/sdk/.temp
    mkdir -p ~/.local/android/sdk/cmdline-tools/latest
    mv ~/.local/android/sdk/.temp/cmdline-tools/* ~/.local/android/sdk/cmdline-tools/latest
    rm -rf ~/.local/android/sdk/.temp

    sudo apt install -y libxcb-cursor0

    echo "Adding ANDROID_HOME to ~/.bashrc..."
    export ANDROID_HOME="$HOME/.local/android/sdk"
    export ANDROID_SDK_ROOT="$ANDROID_HOME"
    export ANDROID_AVD_HOME="$HOME/.local/android/avd"
    export PATH="$PATH:$ANDROID_HOME/emulator:$ANDROID_HOME/platform-tools:$ANDROID_HOME/cmdline-tools/latest/bin"

    # shellcheck disable=SC2016
    appendUniqueLineToBashrc 'export ANDROID_HOME=$HOME/.local/android/sdk'
    # shellcheck disable=SC2016
    appendUniqueLineToBashrc 'export ANDROID_SDK_ROOT=$ANDROID_HOME'
    # shellcheck disable=SC2016
    appendUniqueLineToBashrc 'export ANDROID_AVD_HOME=$HOME/.local/android/avd'
    # shellcheck disable=SC2016
    appendUniqueLineToBashrc 'export PATH=$PATH:$ANDROID_HOME/emulator:$ANDROID_HOME/platform-tools:$ANDROID_HOME/cmdline-tools/latest/bin'

    echo 'y' | sdkmanager "emulator" "platform-tools" "build-tools;36.0.0" "platforms;android-36" "system-images;android-36;google_apis;x86_64"
    echo 'no' | avdmanager create avd --force --name Pixel10_API36 --package "system-images;android-36;google_apis;x86_64"
    # start android emulator with: `emulator -avd Pixel10_API36 -netdelay none -netspeed full`
  else
    echo "[UBUNTU SETUP] Android SDK is already installed. Nothing to do."
  fi
}

function installOpenSshServer() {
  local sftpUser=sftpuser
  local sftpHome="/home/$sftpUser"
  local sshdConfigDropIn=/etc/ssh/sshd_config.d/ubuntu-setup-sftpuser.conf

  echo "[UBUNTU SETUP] Installing OpenSSH Server..."
  sudo apt install -y openssh-server

  if ! id "$sftpUser" &>/dev/null; then
    echo "[UBUNTU SETUP] Creating SFTP-only user '$sftpUser'..."
    sudo useradd -m -d "$sftpHome" -s /usr/sbin/nologin "$sftpUser"
    sudo passwd "$sftpUser"
  else
    echo "[UBUNTU SETUP] SFTP-only user '$sftpUser' already exists."
  fi

  # Configure chroot jail via a managed drop-in file.
  sudo mkdir -p /etc/ssh/sshd_config.d
  cat <<EOF | sudo tee "$sshdConfigDropIn" >/dev/null
Match User sftpuser
    ChrootDirectory /home/sftpuser
    ForceCommand internal-sftp
    AllowTcpForwarding no
    X11Forwarding no
EOF

  # Set proper permissions for the chroot and writable upload directory.
  sudo mkdir -p "$sftpHome"
  sudo chown root:root "$sftpHome"
  sudo chmod 755 "$sftpHome"
  sudo mkdir -p "$sftpHome/uploads"
  sudo chown "$sftpUser:$sftpUser" "$sftpHome/uploads"

  sudo systemctl restart ssh

  # Test the connection from a client:
  # sftp -v sftpuser@localhost
}

function installVeracrypt() {
  if ! command -v veracrypt &>/dev/null; then
    echo "[UBUNTU SETUP] Installing Veracrypt..."
    sudo add-apt-repository ppa:unit193/encryption -y
    sudo apt update
    sudo apt install -y veracrypt
  else
    echo "[UBUNTU SETUP] Veracrypt is already installed. Nothing to do."
  fi
}

function installOllama() {
  if ! command -v ollama &>/dev/null; then
    local graphicsCardName

    echo "[UBUNTU SETUP] Installing Ollama..."
    downloadAndExecute https://ollama.com/install.sh install-ollama.sh 087e24f4444544e4387b669df0bf945cffcbbcdfd7f69e8bc5a980a51b0d2f024e16678b0c1a8f2fcca581f0984153127e75be9d6aa8294a0c97055755e55880

    echo "Adding OLLAMA_AUTH_TOKEN to ~/.bashrc..."
    export OLLAMA_AUTH_TOKEN="ollama"
    appendUniqueLineToBashrc 'export OLLAMA_AUTH_TOKEN="ollama"'

    echo "Adding OLLAMA_MAX_LOADED_MODELS to ~/.bashrc..."
    export OLLAMA_MAX_LOADED_MODELS=1
    appendUniqueLineToBashrc 'export OLLAMA_MAX_LOADED_MODELS=1'

    echo "Adding OLLAMA_KEEP_ALIVE to ~/.bashrc..."
    export OLLAMA_KEEP_ALIVE="5m"
    appendUniqueLineToBashrc 'export OLLAMA_KEEP_ALIVE="5m"'

    graphicsCardName=$(lspci | grep -i 'vga\|3d\|display' | grep -ioE '\[([A-Za-z0-9 ]+)\]' | sed -E 's/^\[(.+)\]$/\1/')

    if lspci | grep -i 'vga\|3d\|display' | grep -q '[GeForce RTX 2070 SUPER]'; then
      echo "[UBUNTU SETUP] Installing Qwen3-Coder (14B with Q4_K_M quantization; 4-bit, optimized for efficiency and performance) model for agentic coding..."
      ollama pull "$UBUNTU_SETUP_PREFERRED_MODEL"
      ollama list
    else
      local encodedGraphicsCardName

      # shellcheck disable=SC2001
      encodedGraphicsCardName=$(echo "$graphicsCardName" | sed 's/ /+/g')

      echo "[UBUNTU SETUP] Could not auto-detect appropriate Ollama coding model for your graphics card: $graphicsCardName"
      echo "[UBUNTU SETUP] Check out this link to find a suitable model for your hardware setup: https://search.brave.com/ask?q=Best+Ollama+coding+model+for+$encodedGraphicsCardName+in+$(date +%Y)"
    fi
  else
    echo "[UBUNTU SETUP] Ollama is already installed."
  fi
}

function installOpenCode() {
  if ! command -v opencode &>/dev/null; then
    echo "[UBUNTU SETUP] Installing OpenCode..."
    downloadAndExecute https://opencode.ai/install install-opencode.sh 5627a0f3ddb896405929cb7718d00df8c0be33a228318106c091b4d553ef48623c1a7d9fe3ccdedb9509f6e4f89e1daf5451c181f6fe51b976ac5c2a6bcb7fe3

    if ! [ -d ~/.config/opencode ]; then
      mkdir ~/.config/opencode
    fi

    # shellcheck disable=SC2016
    echo '{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "ollama": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Ollama (local)",
      "options": {
        "baseURL": "http://localhost:11434/v1"
      },
      "models": {
        "'"$UBUNTU_SETUP_PREFERRED_MODEL"'": {
          "name": "Qwen2.5 Coder 7B (4k context)"
        }
      }
    }
  }
}' | tee ~/.config/opencode/opencode.json

    echo "You can now launch OpenCode via Ollama by running: ollama launch opencode --model $UBUNTU_SETUP_PREFERRED_MODEL"
  else
    echo "[UBUNTU SETUP] OpenCode is already installed."
  fi
}

function installClaudeCode() {
  if ! command -v claude &>/dev/null; then
    echo "[UBUNTU SETUP] Installing Claude Code..."
    downloadAndExecute https://claude.ai/install.sh install-claude.sh c48fd1767e189e15ad6cf0293528cc55c078ff89ff25951a7cb0212e3e99792b288ea54fa33f23a54832f1c7f758551cd44f8b8ae6b4a98e6ce22ae8a1bbddac

    if ! [ -d ~/.claude ]; then
      mkdir ~/.claude
    fi

    echo '{
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "ollama",
    "ANTHROPIC_BASE_URL": "http://localhost:11434",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
    "CLAUDE_CODE_ATTRIBUTION_HEADER": "0"
  }
}' | tee ~/.claude/settings.json

    echo "You can now launch Claude Code via Ollama by running: ollama launch claude --model $UBUNTU_SETUP_PREFERRED_MODEL"
  else
    echo "[UBUNTU SETUP] Claude Code is already installed."
  fi
}

function installNodeJs() {
  if ! command -v fnm &>/dev/null; then
    echo "[UBUNTU SETUP] Installing Fast Node Manager (fnm)..."
    downloadAndExecute https://fnm.vercel.app/install install-fnm.sh 1cd47ee9579b492dffe2ed081e4e9178353a6f08b37fdc15c2b3fae983f1789ab27b96dc71907e36cbb7da774767c38cf6bd7c57baf88396cb8ddf2374b2aa58

    # install script already registered fnm in ~/.bashrc for us,
    # but for whatever reason we cannot source it the current session
    PATH=$PATH:~/.local/share/fnm

    if ! command -v fnm; then
      echo "Failed to install Fast Node Manager (fnm). Abort."
      exit 1
    fi

    if command -v fish && [ -d ~/.config/fish/conf.d/ ]; then
      echo "Adding FNM env vars to Fish shell config..."
      fnm env --use-on-cd --shell fish >>~/.config/fish/conf.d/fnm.fish
    fi
    if command -v zsh &>/dev/null; then
      echo "Adding FNM env vars to ~/.zshrc..."
      fnm env --use-on-cd --shell zsh >>~/.zshrc
    fi
  else
    echo "[UBUNTU SETUP] Fast Node Manager (fnm) is already installed."
  fi

  if ! command -v node &>/dev/null || [[ "$(node -v)" != "v24."* ]]; then
    echo "[UBUNTU SETUP] Installing and activating Node.js 24 via fnm..."
    fnm install 24
    fnm alias 24 default
    fnm use 24
  else
    echo "[UBUNTU SETUP] Node.js 24 is already installed via fnm, nothing to do."
  fi
}

function installGodot() {
  if ! command -v gdvm &>/dev/null; then
    echo "[UBUNTU SETUP] Installing Godot Version Manager (gdvm)..."
    downloadAndExecute https://gdvm.io/install.sh install-gdvm.sh 66d6aa651ff5bbe149e4d8ac6f21e61da799ffd328b359c13efed5adddae3ac7feb5fc6525e71ae3bd96d983a71a4c51ec90600333cca34d1edbc6ff64d85f3c
    # TODO find a way to suppress user prompt (should choose 'N')

    # install script already registered fnm in ~/.bashrc for us,
    # but for whatever reason we cannot source it the current session
    PATH=$PATH:~/.gdvm/bin

    if ! command -v gdvm; then
      echo "Failed to install Godot Version Manager (gdvm). Abort."
      exit 1
    fi
  else
    echo "[UBUNTU SETUP] Godot Version Manager (gdvm) is already installed."
  fi

  if ! command -v godot &>/dev/null || [[ "$(godot --version 2>/dev/null)" != "4.5."* ]]; then
    local currentGodotExec
    local currentGodotHome

    echo "[UBUNTU SETUP] Installing and activating Godot 4.5 via gdvm..."
    gdvm use 4.5

    currentGodotExec=$(gdvm show)
    currentGodotHome=$(dirname "$currentGodotExec")

    # add hard link to Godot executable so tools can find it
    ln "$currentGodotExec" "$currentGodotHome/godot"

    echo "Adding GODOT_HOME to ~/.bashrc..."
    export GODOT_HOME="$currentGodotHome"
    appendUniqueLineToBashrc 'export GODOT_HOME="'"$currentGodotHome"'"'
  else
    echo "[UBUNTU SETUP] Godot 4.5 is already installed via gdvm, nothing to do."
  fi
}

function installRust() {
  if ! command -v rustup &>/dev/null; then
    echo "[UBUNTU SETUP] Installing Rustup..."
    sudo apt install -y curl

    # TODO use downloadAndExecute with checksum instead
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    # shellcheck disable=SC1090
    source ~/.cargo/env

    rustup update
    rustup default stable
  else
    echo "[UBUNTU SETUP] Rust is already installed. Nothing to do."
  fi
}

function installGit() {
  if ! command -v git &>/dev/null; then
    echo "[UBUNTU SETUP] Installing Git..."
    sudo apt install -y git fish zsh
    reconfigureGit
  else
    echo "[UBUNTU SETUP] Git is already installed. Nothing to do."
  fi
}

function installDevTools() {
  echo "[UBUNTU SETUP] Installing essential dev-tools..."
  sudo apt install -y build-essential gdb lldb shfmt

  installGit
  installNodeJs
  installVsCode

  if [[ "${UBUNTU_SETUP_LENAS_SETUP:-}" == "1" ]]; then
    installRust
    installJava
    installGradle
    installAndroidSdk
    installGodot
  fi
}

function installGnomeShell() {
  echo "[UBUNTU SETUP] Installing gnome-shell and related utilities..."
  sudo apt install -y ubuntu-gnome-desktop gnome-shell-extension-manager gnome-browser-connector gnome-tweaks dconf-editor alacarte
  configureGnomeSettings
}

function startUbuntuSetup() {
  if [[ "${UBUNTU_SETUP_BASIC_SETUP:-}" == "1" ]]; then
    echo "[UBUNTU SETUP] Starting basic setup for user ${UBUNTU_SETUP_USERNAME:-}..."
  elif [[ "${UBUNTU_SETUP_LENAS_SETUP:-}" == "1" ]]; then
    echo "[UBUNTU SETUP] Starting setup for Lena <3..."
  fi

  echo "[UBUNTU SETUP] Updating packages..."
  sudo apt update

  # set up the basics
  installFlatpak
  installGnomeShell
  installSystemUtils
  installMultimediaUtils
  installCommandlineBasics

  # disable useless snapshots for snap packages to safe time
  sudo snap set system snapshots.automatic.retention=no
  # install snap packages
  installDiscord
  installSpotify
  installThunderbird

  # install flatpak packages
  installVlc
  installGimp
  installInkscape
  if [[ "${UBUNTU_SETUP_LENAS_SETUP:-}" == "1" ]]; then
    installBlender
    installElement
  fi

  # install apt packages
  installTorBrowser
  if [[ "${UBUNTU_SETUP_LENAS_SETUP:-}" == "1" ]]; then
    installBrave
    installSignal
    installVeracrypt
  fi

  # install gaming setup
  installSteam
  if [[ "${UBUNTU_SETUP_LENAS_SETUP:-}" == "1" ]]; then
    installAzahar
    installMupen64Plus
  fi

  # install fonts
  installMsFonts
  if [[ "${UBUNTU_SETUP_LENAS_SETUP:-}" == "1" ]]; then
    installCustomFonts
  fi

  # install dev tools
  installDevTools

  # set up UFW (Uncomplicated Firewall)
  configureFirewall

  sudo apt update
  sudo apt upgrade -y
  sudo apt autoremove -y

  sudo snap refresh
  flatpak uninstall -y --unused
  flatpak update -y --noninteractive

  echo "[UBUNTU SETUP] Setup complete!"
  exit 0
}

function printHelpText() {
  echo "Usage: ./ubuntu-setup.sh [OPTION]"
  echo "Installs and configures Ubuntu."
  echo
  echo "  -h, --help                      prints this help text"
  echo "  --basic-setup                   run only essential install and configure only the most relevant options"
  echo "  --lenas-setup                   run full install and configure all available options (except for openssh-server)"
  echo "  --install-ollama                installs Ollama and sets up AI models and VSCode integration"
  echo "  --install-godot                 installs Godot 4.5 via Godot Version Manager (gdvm)"
  echo "  --install-openssh-server        installs openssh-server for local testing"
  echo "  --configure-gsettings           configures useful GNOME settings"
  echo "  --configure-lenas-gsettings     same as --configure-gsettings, but with private extra settings for Lena <3"
  echo "  --reconfigure-git               deletes local git config and reconfigures it from scratch"
  echo "  --reconfigure-lenas-git         same as --reconfigure-git, but with private extra settings for Lena <3"
  echo "  --reconfigure-vscode            deletes local VSCode config and reconfigures it from scratch"
  echo "  --reconfigure-lenas-vscode      same as --reconfigure-vscode, but with private extra settings for Lena <3"
}

## MAIN ##
if [ $# -eq 0 ]; then
  echo "Missing arguments."
  echo
  printHelpText
  exit 1
fi

for arg in "$@"; do
  if [[ "$arg" == "-h" ]] || [[ "$arg" == "--help" ]]; then
    printHelpText
    exit 0
  elif [[ "$arg" == "--basic-setup" ]]; then
    UBUNTU_SETUP_BASIC_SETUP=1
  elif [[ "$arg" == "--lenas-setup" ]]; then
    UBUNTU_SETUP_LENAS_SETUP=1
  elif [[ "$arg" == "--reconfigure-git" ]]; then
    UBUNTU_SETUP_RECONFIGURE_GIT=1
  elif [[ "$arg" == "--reconfigure-lenas-git" ]]; then
    UBUNTU_SETUP_RECONFIGURE_LENAS_GIT=1
  elif [[ "$arg" == "--reconfigure-vscode" ]]; then
    UBUNTU_SETUP_RECONFIGURE_VSCODE=1
  elif [[ "$arg" == "--reconfigure-lenas-vscode" ]]; then
    UBUNTU_SETUP_RECONFIGURE_LENAS_VSCODE=1
  elif [[ "$arg" == "--configure-gsettings" ]]; then
    UBUNTU_SETUP_CONFIGURE_GSETTINGS=1
  elif [[ "$arg" == "--configure-lenas-gsettings" ]]; then
    UBUNTU_SETUP_CONFIGURE_LENAS_GSETTINGS=1
  elif [[ "$arg" == "--install-ollama" ]]; then
    UBUNTU_SETUP_INSTALL_OLLAMA=1
  elif [[ "$arg" == "--install-godot" ]]; then
    UBUNTU_SETUP_INSTALL_GODOT=1
  elif [[ "$arg" == "--install-openssh-server" ]]; then
    UBUNTU_SETUP_INSTALL_OPENSSH_SERVER=1
  else
    echo "Unknown argument: $arg"
    echo
    printHelpText
    exit 1
  fi
done

UBUNTU_SETUP_USERNAME=$(id -un)

if [[ -n "$BASH_VERSION" ]]; then
  echo "[UBUNTU SETUP] Script is running in Bash ($BASH_VERSION)."
else
  echo "[UBUNTU SETUP] Script is not running in Bash. Abort."
  exit 1
fi
if [ $EUID -eq 0 ]; then
  echo "[UBUNTU SETUP] This script is not intended to be run as root! Run as local user instead! Abort."
  exit 1
else
  echo "[UBUNTU SETUP] Running as user '${UBUNTU_SETUP_USERNAME:-}'."
fi
if [[ "$(lsb_release -si 2>/dev/null)" != "Ubuntu" ]]; then
  echo "[UBUNTU SETUP] Your linux distribution $(lsb_release -si 2>/dev/null) is not supported! Abort."
  exit 1
fi
if [[ "$(lsb_release -sr 2>/dev/null)" != "24.04" ]]; then
  echo "[UBUNTU SETUP] Your Ubuntu version is not supported $(lsb_release -sr 2>/dev/null)! Abort."
  exit 1
else
  echo "[UBUNTU SETUP] Running on $(lsb_release -sd 2>/dev/null)."
fi

if [[ "${UBUNTU_SETUP_RECONFIGURE_GIT:-}" == "1" ]] || [[ "${UBUNTU_SETUP_RECONFIGURE_LENAS_GIT:-}" == "1" ]]; then
  reconfigureGit
fi

if [[ "${UBUNTU_SETUP_RECONFIGURE_VSCODE:-}" == "1" ]] || [[ "${UBUNTU_SETUP_RECONFIGURE_LENAS_VSCODE:-}" == "1" ]]; then
  reconfigureVsCode
fi

if [[ "${UBUNTU_SETUP_CONFIGURE_GSETTINGS:-}" == "1" ]] || [[ "${UBUNTU_SETUP_CONFIGURE_LENAS_GSETTINGS:-}" == "1" ]]; then
  configureGnomeSettings
fi

if [[ "${UBUNTU_SETUP_INSTALL_OLLAMA:-}" == "1" ]]; then
  if [[ "${UBUNTU_SETUP_BASIC_SETUP:-}" == "1" ]]; then
    echo "Error: option --install-ollama is mutually exclusive with option --basic-setup"
    exit 1
  elif [[ "${UBUNTU_SETUP_LENAS_SETUP:-}" == "1" ]]; then
    echo "Error: option --install-ollama is mutually exclusive with option --lenas-setup"
    exit 1
  else
    UBUNTU_SETUP_PREFERRED_MODEL="qwen2.5-coder:7b-instruct-q4_K_M"

    installOllama
    installOpenCode
    installClaudeCode
    installVsCode
  fi
fi

if [[ "${UBUNTU_SETUP_INSTALL_GODOT:-}" == "1" ]]; then
  if [[ "${UBUNTU_SETUP_BASIC_SETUP:-}" == "1" ]]; then
    echo "Error: option --install-godot is mutually exclusive with option --basic-setup"
    exit 1
  elif [[ "${UBUNTU_SETUP_LENAS_SETUP:-}" == "1" ]]; then
    echo "Error: option --install-godot is mutually exclusive with option --lenas-setup"
    exit 1
  else
    installGodot
  fi
fi

if [[ "${UBUNTU_SETUP_INSTALL_OPENSSH_SERVER:-}" == "1" ]]; then
  if [[ "${UBUNTU_SETUP_BASIC_SETUP:-}" == "1" ]]; then
    echo "Error: option --install-openssh-server is mutually exclusive with option --basic-setup"
    exit 1
  elif [[ "${UBUNTU_SETUP_LENAS_SETUP:-}" == "1" ]]; then
    echo "Error: option --install-openssh-server is mutually exclusive with option --lenas-setup"
    exit 1
  else
    installOpenSshServer
  fi
fi

if [[ "${UBUNTU_SETUP_BASIC_SETUP:-}" == "1" ]] && [[ "${UBUNTU_SETUP_LENAS_SETUP:-}" == "1" ]]; then
  echo "Error: option --basic-setup is mutually exclusive with option --lenas-setup"
  exit 1
elif [[ "${UBUNTU_SETUP_BASIC_SETUP:-}" == "1" ]] || [[ "${UBUNTU_SETUP_LENAS_SETUP:-}" == "1" ]]; then
  startUbuntuSetup
fi
