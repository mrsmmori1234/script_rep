#!/bin/bash

# --- Settings ---
# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# Path to python in venv (Update as per your environment)
PYTHON_BIN="/home/mrsmmori/.pyenv/versions/scripts-env/bin/python"
# Path to the Python script
PY_SCRIPT="$SCRIPT_DIR/make_playlist.py"

# --- 1. Argument Check ---
if [ $# -eq 0 ]; then
    echo "Usage: $0 [-r] [target_directory]"
    exit 1
fi

SHUFFLE_OPT=""
TARGET_DIR_INPUT=""

for arg in "$@"; do
    case $arg in
        -r|--random)
            SHUFFLE_OPT="-r"
            ;;
        *)
            if [ -z "$TARGET_DIR_INPUT" ]; then
                TARGET_DIR_INPUT="$arg"
            fi
            ;;
    esac
done

if [ -z "$TARGET_DIR_INPUT" ]; then
    echo "Usage: $0 [-r] [target_directory]"
    exit 1
fi
TARGET_DIR=$(realpath "$TARGET_DIR_INPUT") 2>/dev/null || { echo "Error: Could not resolve path"; exit 1; }

# --- 2. Validation ---
if [ ! -d "$TARGET_DIR" ]; then
    echo "Error: '$TARGET_DIR' is not a valid directory."
    exit 1
fi

if [ ! -f "$PYTHON_BIN" ]; then
    echo "Error: Python environment not found: $PYTHON_BIN"
    exit 1
fi

PARENT_DIR=$(dirname "$TARGET_DIR")

# --- 3. Execution ---
echo "Creating playlist for: $TARGET_DIR"

# Move to parent directory to create the output file there
cd "$PARENT_DIR" || { echo "Error: Could not change directory to: $PARENT_DIR"; exit 1; }

# Execute Python script
"$PYTHON_BIN" "$PY_SCRIPT" "$TARGET_DIR" ${SHUFFLE_OPT}
EXIT_CODE=$?

# --- 4. Result Check and VLC Launch Option ---
if [ $EXIT_CODE -eq 0 ]; then
    PLAYLIST_FILE="$PARENT_DIR/$(basename "$TARGET_DIR").xspf"
    
    echo "---------------------------------------"
    echo "Completed: $PLAYLIST_FILE"
    echo "---------------------------------------"
    
    # Optional: Confirm whether to play in VLC immediately
    #read -p "今すぐVLCで再生しますか？ (y/N): " yn
    #case $yn in
    #    [Yy]* ) vlc "$PLAYLIST_FILE" & ;;
    #    * ) echo "終了します。";;
    #esac
else
    echo "An error occurred."
    exit 1
fi
exit $EXIT_CODE