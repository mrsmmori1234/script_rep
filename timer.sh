#!/bin/bash

# Check argument
if [ -z "$1" ]; then
    echo "Usage: $0 <minutes>"
    echo "Example: $0 25 (25-minute timer)"
    exit 1
fi

total_seconds=$(( $1 * 60 ))
remaining=$total_seconds
bar_width=30
target_min="$1"

# --- ユーザー名に依存しない相対パスの設定 ---
# スクリプトが存在するディレクトリの絶対パスを自動取得
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# scriptsディレクトリの1つ上の階層にある notebooks/outputs/ を指定
csv_file="$SCRIPT_DIR/../notebooks/outputs/focustime.csv"

# Ensure CSV directory exists
mkdir -p "$(dirname "$csv_file")"

# If CSV does not exist, create header
if [ ! -f "$csv_file" ]; then
    echo "Timestamp,Minutes" > "$csv_file"
fi

echo "=== Timer Started: $target_min min ==="
echo "Controls: Press 'p' to Pause/Resume, 'q' to Quit"

paused=0

while [ $remaining -gt 0 ]; do
    # Check for key input (non-blocking)
    read -t 1 -n 1 key
    if [ "$key" = "p" ] || [ "$key" = "P" ]; then
        if [ $paused -eq 0 ]; then
            paused=1
            echo -e "\n--- Timer Paused (Press 'p' to resume) ---"
        else
            paused=0
            echo -e "--- Timer Resumed ---"
        fi
    elif [ "$key" = "q" ] || [ "$key" = "Q" ]; then
        echo -e "\nTimer cancelled."
        exit 0
    fi

    if [ $paused -eq 1 ]; then
        sleep 1
        continue
    fi

    min=$(( remaining / 60 ))
    sec=$(( remaining % 60 ))

    elapsed=$(( total_seconds - remaining ))
    filled=$(( elapsed * bar_width / total_seconds ))
    empty=$(( bar_width - filled ))

    bar=$(printf "%0.s#" $(seq 1 $filled 2>/dev/null))
    spaces=$(printf "%0.s-" $(seq 1 $empty 2>/dev/null))

    printf "\r[%s%s] %02d:%02d Remaining" "$bar" "$spaces" "$min" "$sec"

    remaining=$(( remaining - 1 ))
done

printf "\r[%s] 00:00 Finished!                     \n" "$(printf "%0.s#" $(seq 1 $bar_width))"

# Play pleasant Windows chime (if powershell is available)
if command -v powershell.exe &> /dev/null; then
    powershell.exe -c "(New-Object Media.SoundPlayer 'C:\Windows\Media\Windows Background.wav').PlaySync()" 2>/dev/null
fi

echo "Time is up! Great job."

# Record focus time to CSV (Timestamp, Minutes)
timestamp=$(date "+%Y-%m-%d %H:%M:%S")
echo "$timestamp,$target_min" >> "$csv_file"
echo "Recorded focus time to: $csv_file"
