#!/bin/bash
function downloadAndVerify() {
  local url=$1
  local fileName=$2
  local controlHash=$3
  local useTempFile=$4

  local downloadFile
  local fileHash

  if ! command -v wget &>/dev/null; then
    sudo apt install -y wget
  fi
  if ! command -v rhash &>/dev/null; then
    sudo apt install -y rhash
  fi

  if [ "$useTempFile" == "true" ]; then
    downloadFile=$(mktemp --suffix=".$fileName")
  else
    downloadFile="$HOME/Downloads/$fileName"
  fi

  if [ -f "$downloadFile" ]; then
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
  local url=$1
  local fileName=$2
  local controlHash=$3
  local runAsRoot=$4

  downloadAndVerify "$1" "$2" "$3"
  local tempFile=$UBUNTU_SETUP_LAST_DOWNLOADED_FILE

  echo "Making file executable..."
  chmod +x "$tempFile"

  echo "Executing file..."
  if [[ "$runAsRoot" == "true" ]]; then
    sudo "$tempFile"
  else
    # shellcheck disable=SC1090
    . "$tempFile"
  fi
}

function configureGnomeSettings() {
  echo "[UBUNTU SETUP] Adjust GNOME user settings for Nautilus..."
  gsettings set org.gnome.nautilus.preferences default-sort-order 'type'
  gsettings set org.gnome.nautilus.preferences show-create-link true

  echo "[UBUNTU SETUP] Adjust GNOME user settings for Gedit..."
  gsettings set org.gnome.gedit.preferences.editor display-line-numbers true
  gsettings set org.gnome.gedit.preferences.editor highlight-current-line true
  gsettings set org.gnome.gedit.preferences.editor bracket-matching true
  gsettings set org.gnome.gedit.preferences.editor scheme 'oblivion'
  gsettings set org.gnome.gedit.preferences.editor auto-indent true
  gsettings set org.gnome.gedit.preferences.editor insert-spaces true
  gsettings set org.gnome.gedit.preferences.editor tabs-size 'uint32 2'

  echo "[UBUNTU SETUP] Adjust GNOME user settings to disable new tiling feature..."
  gsettings set org.gnome.mutter.keybindings toggle-tiled-left "['<Super>Left']"
  gsettings set org.gnome.mutter.keybindings toggle-tiled-right "['<Super>Right']"

  echo "[UBUNTU SETUP] Adjust GNOME user settings to disable default shortcuts that interfere with VSCode..."
  gsettings set org.gnome.desktop.wm.keybindings toggle-shaded "[]"
  gsettings set org.gnome.desktop.wm.keybindings begin-move "[]"
  gsettings set org.gnome.desktop.wm.keybindings panel-main-menu "[]"

  #gsettings set org.gnome.desktop.wm.keybindings move-to-workspace-right "[]"
  #gsettings set org.gnome.desktop.wm.keybindings move-to-workspace-left "[]"
  #gsettings set org.gnome.desktop.wm.keybindings move-to-workspace-down "['<Super><Shift>Page_Down']"
  #gsettings set org.gnome.desktop.wm.keybindings move-to-workspace-up "['<Super><Shift>Page_Up']"

  #echo "[UBUNTU SETUP] Set mouse acceleration profile to 'flat' to avoid drag and drop issues..."
  #gsettings set org.gnome.desktop.peripherals.mouse accel-profile 'flat'
  #gsettings set org.gnome.desktop.peripherals.mouse speed 'double 1.0'
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
  if ! command -v nvm &>/dev/null; then
    installNodeJs
    # shellcheck disable=SC1090
    source ~/.nvm/nvm.sh
  fi

  installCustomFonts

  node_24=$(nvm which 24)

  echo "Installing commonly used VSCode extensions..."
  code --install-extension vscode-icons-team.vscode-icons
  code --install-extension ms-vsliveshare.vsliveshare
  code --install-extension ms-playwright.playwright
  code --install-extension editorconfig.editorconfig
  code --install-extension sanaajani.taskrunnercode
  code --install-extension eamodio.gitlens
  code --install-extension esbenp.prettier-vscode
  code --install-extension dbaeumer.vscode-eslint
  code --install-extension rust-lang.rust-analyzer
  code --install-extension ms-python.python
  code --install-extension charliermarsh.ruff
  code --install-extension mads-hartmann.bash-ide-vscode
  code --install-extension timonwong.shellcheck
  code --install-extension mkhl.shfmt
  code --install-extension dohe.godot-format
  code --install-extension geequlim.godot-tools

  echo "Installing VSCode themes..."
  code --install-extension atomiks.moonlight

  echo "Configuring basic user settings for VSCode..."
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
}

function installCommandlineBasics() {
  echo "[UBUNTU SETUP] Install basic command line utilities..."
  sudo apt install -y fish plocate rhash curl pwgen optipng rar p7zip-full pdftk-java mesa-utils apt-transport-https
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
  local fontName=$1
  local fontType=$2
  local fontDirectoryName=$3
  local url=$4
  local fileName=$5
  local controlHash=$6

  local fontDirectory="/usr/share/fonts/$fontType/$fontDirectoryName"

  if ! [ -d "$fontDirectory" ]; then
    local fontSuffix

    if [ "$fontType" == "opentype" ]; then
      fontSuffix="*.otf"
    elif [ "$fontType" == "truetype" ]; then
      fontSuffix="*.ttf"
    else
      echo "Invalid font type: $fontType"
      exit 1
    fi

    echo "[UBUNTU SETUP] Downloading and installing $fontType font '$fontName'..."
    downloadAndVerify "$url" "$fileName" "$controlHash"
    sudo mkdir "$fontDirectory"
    sudo unzip -d "$fontDirectory" -j "$UBUNTU_SETUP_LAST_DOWNLOADED_FILE" "$fontSuffix"

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

  if [ "$UBUNTU_SETUP_CUSTOM_FONT_INSTALLED" == "1" ]; then
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
    sudo snap install code --classic
    reconfigureVsCode
  else
    echo "[UBUNTU SETUP] VSCode is already installed. Nothing to do."
  fi
}

function installFlatpak() {
  if ! command -v flatpak &>/dev/null; then
    echo "[UBUNTU SETUP] Installing Flatpak..."
    sudo apt install -y flatpak gnome-software-plugin-flatpak

    flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
    flatpak remote-add --user --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo

    flatpak update
    flatpak update --appstream
  else
    echo "[UBUNTU SETUP] Flatpak is already installed. Nothing to do."
  fi
}

function installVlc() {
  if ! command -v vlc &>/dev/null; then
    echo "[UBUNTU SETUP] Installing VLC Player..."
    installFlatpak

    if ! flatpak info org.videolan.VLC &>/dev/null; then
      flatpak install -y --user flathub org.videolan.VLC
    fi
  else
    echo "[UBUNTU SETUP] VLC Player is already installed. Nothing to do."
  fi
}

function installSignal() {
  if ! command -v signal-desktop &>/dev/null; then
    echo "[UBUNTU SETUP] Installing Signal..."
    installFlatpak

    if ! flatpak info org.signal.Signal &>/dev/null; then
      flatpak install -y --user flathub org.signal.Signal
    fi
  else
    echo "[UBUNTU SETUP] Signal is already installed. Nothing to do."
  fi
}

function installElement() {
  if ! command -v element-desktop &>/dev/null; then
    echo "[UBUNTU SETUP] Installing Element..."
    installFlatpak

    if ! flatpak info im.riot.Riot &>/dev/null; then
      flatpak install -y --user flathub im.riot.Riot
      # The Flatpak version requires specific permissions for file access. By default, it may not access your files.
      # To allow access to common directories like Pictures, Videos, and Documents, use:
      # flatpak override --filesystem=xdg-pictures --filesystem=xdg-videos --filesystem=xdg-documents im.riot.Riot
    fi
  else
    echo "[UBUNTU SETUP] Element is already installed. Nothing to do."
  fi
}

function installInkscape() {
  if ! command -v inkscape &>/dev/null; then
    echo "[UBUNTU SETUP] Installing Inkscape..."
    installFlatpak

    if ! flatpak info org.inkscape.Inkscape &>/dev/null; then
      flatpak install -y --user flathub org.inkscape.Inkscape
    fi
  else
    echo "[UBUNTU SETUP] Inkscape is already installed. Nothing to do."
  fi
}

function installGimp() {
  if ! command -v gimp &>/dev/null; then
    echo "[UBUNTU SETUP] Installing Gimp..."
    installFlatpak

    if ! flatpak info org.gimp.GIMP &>/dev/null; then
      flatpak install -y --user https://flathub.org/repo/appstream/org.gimp.GIMP.flatpakref
    fi
  else
    echo "[UBUNTU SETUP] Gimp is already installed. Nothing to do."
  fi
}

function installProtonUp() {
  installFlatpak

  if ! flatpak info net.davidotek.pupgui2 &>/dev/null; then
    echo "[UBUNTU SETUP] Installing ProtonUp-Qt..."
    flatpak install flathub net.davidotek.pupgui2
  else
    echo "[UBUNTU SETUP] ProtonUp-Qt is already installed. Nothing to do."
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
    echo >>~/.bashrc
    # shellcheck disable=SC2016
    echo 'export JAVA_HOME=$(readlink -f /usr/bin/javac | sed "s:/bin/javac::")' | tee -a ~/.bashrc

    # shellcheck disable=SC1090
    source ~/.bashrc
  else
    echo "[UBUNTU SETUP] Java is already installed. Nothing to do."
  fi
}

function installGradle() {
  if ! command -v gradle &>/dev/null; then
    echo "[UBUNTU SETUP] Installing Gradle..."
    sudo apt install -y gradle

    echo "Adding GRADLE_HOME to ~/.bashrc..."
    echo >>~/.bashrc
    # shellcheck disable=SC2016
    echo 'export GRADLE_HOME=$(readlink -f /usr/bin/gradle | sed "s:/bin/gradle::")' | tee -a ~/.bashrc

    # shellcheck disable=SC1090
    source ~/.bashrc
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
    unzip "$UBUNTU_SETUP_LAST_DOWNLOADED_FILE" -d ~/.local/android/sdk/.temp
    mkdir -p ~/.local/android/sdk/cmdline-tools/latest
    mv ~/.local/android/sdk/.temp/cmdline-tools/* ~/.local/android/sdk/cmdline-tools/latest
    rm -rf ~/.local/android/sdk/.temp

    sudo apt install -y libxcb-cursor0

    echo "Adding ANDROID_HOME to ~/.bashrc..."
    # shellcheck disable=SC2016
    echo 'export ANDROID_HOME=$HOME/.local/android/sdk' | tee -a ~/.bashrc
    # shellcheck disable=SC2016
    echo 'export ANDROID_SDK_ROOT=$ANDROID_HOME' | tee -a ~/.bashrc
    # shellcheck disable=SC2016
    echo 'export ANDROID_AVD_HOME=$HOME/.local/android/avd' | tee -a ~/.bashrc
    echo >>~/.bashrc
    # shellcheck disable=SC2016
    echo 'export PATH=$PATH:$ANDROID_HOME/emulator:$ANDROID_HOME/platform-tools:$ANDROID_HOME/cmdline-tools/latest/bin' | tee -a ~/.bashrc
    echo >>~/.bashrc

    # shellcheck disable=SC1090
    source ~/.bashrc

    echo 'y' | sdkmanager "emulator" "platform-tools" "build-tools;36.0.0" "platforms;android-36" "system-images;android-36;google_apis;x86_64"
    echo 'no' | avdmanager create avd --force --name Pixel10_API36 --package "system-images;android-36;google_apis;x86_64"
    # start android emulator with: `emulator -avd Pixel10_API36 -netdelay none -netspeed full`
  else
    echo "[UBUNTU SETUP] Android SDK is already installed. Nothing to do."
  fi
}

function installOpenSshServer() {
  if ! [ -d /home/sftpuser ]; then
    echo "[UBUNTU SETUP] Installing OpenSSH Server..."
    sudo apt install -y openssh-server

    # Create an SFTP-only user for restricted access
    sudo useradd -m -d /home/sftpuser -s /usr/sbin/nologin sftpuser
    sudo passwd sftpuser

    # Configure chroot jail (recommended for security)
    echo "
Match User sftpuser
    ChrootDirectory /home/sftpuser
    ForceCommand internal-sftp
    AllowTcpForwarding no
    X11Forwarding no
" | sudo tee -a /etc/ssh/sshd_config

    # restart SSH
    sudo systemctl restart ssh

    # Set proper permissions
    sudo chown root:root /home/sftpuser
    sudo chmod 755 /home/sftpuser
    sudo mkdir /home/sftpuser/uploads
    sudo chown sftpuser:sftpuser /home/sftpuser/uploads

    #Test the connection from a client
    #sftp -v sftpuser@localhost
  else
    echo "[UBUNTU SETUP] OpenSSH Server is already installed. Nothing to do."
  fi
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

function installNodeJs() {
  if ! [ -f ~/.nvm/nvm.sh ]; then
    echo "[UBUNTU SETUP] Installing Node Version Manager (nvm)..."
    downloadAndExecute https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.4/install.sh nvm-install.sh a8e082d8d1a9b61a09e5d3e1902d2930e5b1b84a86f9777c7d2eb50ea204c0141f6a97c54a860bc3282e7b000f1c669c755f5e0db7bd6d492072744c302c0a21

    echo "[UBUNTU SETUP] Installing the latest LTS version of Node.js..."
    # shellcheck disable=SC1090
    source ~/.nvm/nvm.sh
    nvm install --lts
    nvm use --lts
  else
    echo "[UBUNTU SETUP] Node Version Manager (nvm) is already installed. Nothing to do."
  fi
}

function installRust() {
  if ! command -v rustup &>/dev/null; then
    echo "[UBUNTU SETUP] Installing Rustup..."
    sudo apt install -y curl

    # TODO send new line on stdio to skip installer prompt
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
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
    git config --global core.autocrlf input
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
  sudo apt install -y build-essential gdb lldb shfmt

  installGit
  installRust
  installJava
  installGradle
  installNodeJs
  installVsCode
  installAndroidSdk

  #installOpenSshServer
}

function installGnomeShell() {
  echo "[UBUNTU SETUP] Installing gnome-shell and related utilities..."
  sudo apt install -y ubuntu-gnome-desktop gnome-shell-extension-manager gnome-browser-connector gnome-tweaks dconf-editor alacarte
  configureGnomeSettings
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

  # set up the basics
  installFlatpak
  installGnomeShell
  installSystemUtils
  installMultimediaUtils
  installCommandlineBasics

  # install snap packages
  installDiscord
  installSpotify
  installThunderbird

  # install flatpak packages
  installVlc
  installGimp
  installSignal
  installElement
  installInkscape

  # install apt packages
  installBrave
  installSteam
  installTorBrowser
  installVeracrypt

  # install fonts
  installMsFonts
  installCustomFonts

  # install dev tools
  installDevTools

  sudo apt update
  sudo apt upgrade -y
  sudo apt autoremove -y

  sudo snap refresh
  flatpak uninstall -y --unused
  flatpak update

  echo "[UBUNTU SETUP] Setup complete!"
  exit 0
}

## MAIN ##
startUbuntuSetup
