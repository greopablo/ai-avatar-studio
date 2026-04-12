#!/bin/bash
# Simple auto-sync without GitHub push
# For when GitHub SSH is not configured

PROJECT_DIR="/opt/ai-department/rustore-launch"
LOG_FILE="$PROJECT_DIR/perpetual_motion.log"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === SYNC CYCLE ===" >> "$LOG_FILE"

cd "$PROJECT_DIR"

# Add all changes
git add -A

# Commit if there are changes
if ! git diff --cached --quiet; then
    git commit -m "chore: auto-sync $(date '+%Y-%m-%d %H:%M')"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Committed changes" >> "$LOG_FILE"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] No changes" >> "$LOG_FILE"
fi

# Update progress timestamp
if [ -f PROGRESS_REPORT.txt ]; then
    sed -i "s/Последнее обновление:.*/Последнее обновление: $(date '+%Y-%m-%d %H:%M:%S') UTC/" PROGRESS_REPORT.txt
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === SYNC COMPLETE ===" >> "$LOG_FILE"
