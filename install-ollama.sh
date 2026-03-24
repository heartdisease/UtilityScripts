#!/bin/bash
IFS=$'\n\t'
set -euo pipefail

function downloadAndVerify() {
  local url=${1:-}
  local fileName=${2:-}
  local controlHash=${3:-}

  local downloadFile
  local fileHash

  if ! command -v wget &>/dev/null; then
    if command -v apt &>/dev/null; then
      # Ubuntu
      sudo apt install -y wget
    else
      # MacOS X
      brew install wget
    fi
  fi
  if ! command -v rhash &>/dev/null; then
    if command -v apt &>/dev/null; then
      # Ubuntu
      sudo apt install -y rhash
    else
      # MacOS X
      brew install rhash
    fi
  fi

  downloadFile=$(mktemp --suffix=".$fileName")

  echo "Downloading '$url' to '$downloadFile'..."
  wget "$url" -qO "$downloadFile"

  fileHash=$(rhash --sha512 "$downloadFile" | grep -oE '^\w+')

  if [[ "$fileHash" == "$controlHash" ]]; then
    echo "File hash matches ($url --> $downloadFile)! [sha512.$fileHash]"
    OLLAMA_SETUP_LAST_DOWNLOADED_FILE=$downloadFile
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

  downloadAndVerify "$url" "$fileName" "$controlHash"
  local tempFile=${OLLAMA_SETUP_LAST_DOWNLOADED_FILE:-}

  echo "Making file executable..."
  chmod +x "$tempFile"

  echo "Executing file '$tempFile'..."
  bash "$tempFile"
}

function appendUniqueLineToBashrc() {
  local line=${1:-}
  local bashrc="$HOME/.bashrc"

  touch "$bashrc"
  if ! grep -Fqx "$line" "$bashrc"; then
    printf '%s\n' "$line" >>"$bashrc"
  fi
}

function installOllama() {
  if ! command -v ollama &>/dev/null; then
    echo "[OLLAMA SETUP] Installing Ollama..."
    downloadAndExecute https://ollama.com/install.sh install-ollama.sh 087e24f4444544e437b669df0bf945cffcbbcdfd7f69e8bc5a980a51b0d2f024e16678b0c1a8f2fcca581f0984153127e75be9d6aa8294a0c97055755e55880

    echo "Adding OLLAMA_AUTH_TOKEN to ~/.bashrc..."
    export OLLAMA_AUTH_TOKEN="ollama"
    appendUniqueLineToBashrc 'export OLLAMA_AUTH_TOKEN="ollama"'

    echo "Adding OLLAMA_MAX_LOADED_MODELS to ~/.bashrc..."
    export OLLAMA_MAX_LOADED_MODELS=1
    appendUniqueLineToBashrc 'export OLLAMA_MAX_LOADED_MODELS=1'

    echo "Adding OLLAMA_KEEP_ALIVE to ~/.bashrc..."
    export OLLAMA_KEEP_ALIVE="5m"
    appendUniqueLineToBashrc 'export OLLAMA_KEEP_ALIVE="5m"'

    echo "[OLLAMA SETUP] Installing Qwen3-Coder (14B with Q4_K_M quantization; 4-bit, optimized for efficiency and performance) model for agentic coding..."
    ollama pull "$OLLAMA_SETUP_PREFERRED_MODEL"
    ollama list
  else
    echo "[OLLAMA SETUP] Ollama is already installed."
  fi
}

function installOpenCode() {
  if ! command -v opencode &>/dev/null; then
    echo "[OLLAMA SETUP] Installing OpenCode..."
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
        "'"$OLLAMA_SETUP_PREFERRED_MODEL"'": {
          "name": "Qwen2.5 Coder 7B (4k context)"
        }
      }
    }
  }
}' | tee ~/.config/opencode/opencode.json

    echo "You can now launch OpenCode via Ollama by running: ollama launch opencode --model $OLLAMA_SETUP_PREFERRED_MODEL"
  else
    echo "[OLLAMA SETUP] OpenCode is already installed."
  fi
}

function installClaudeCode() {
  if ! command -v claude &>/dev/null; then
    echo "[OLLAMA SETUP] Installing Claude Code..."
    downloadAndExecute https://claude.ai/install.sh install-claude.sh c48fd1767e189e15ad6cf0293528cc55c078ff89ff25951a7cb0212e3e99792b288ea54fa33f23a54832f1c7f758551cd44f8b8ae6b4a98e6ce22ae8a1bbddac

    if ! [ -d ~/.claude ]; then
      mkdir ~/.claude
    fi

    echo '{
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "ollama",
    "ANTHROPIC_API_KEY": "",
    "ANTHROPIC_BASE_URL": "http://localhost:11434",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
    "CLAUDE_CODE_ATTRIBUTION_HEADER": "0"
  }
}' | tee ~/.claude/settings.json

    echo "You can now launch Claude Code via Ollama by running: ollama launch claude --model $OLLAMA_SETUP_PREFERRED_MODEL"
  else
    echo "[OLLAMA SETUP] Claude Code is already installed."
  fi
}

## MAIN ##
OLLAMA_SETUP_PREFERRED_MODEL="qwen2.5-coder:7b-instruct-q4_K_M"

installOllama
installOpenCode
installClaudeCode
