#!/bin/bash
# ============================================================
# AI DEPARTMENT — PERPETUAL MOTION SYSTEM
# Система бесконечного цикла работы агентов
# ============================================================

PROJECT_DIR="/opt/ai-department/rustore-launch"
LOG_FILE="$PROJECT_DIR/caesar_monitor.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$DATE] === CAESAR MONITOR RUN ===" >> "$LOG_FILE"

cd "$PROJECT_DIR"

# 1. CHECK AGENTS STATUS
echo "[$DATE] Checking agents..." >> "$LOG_FILE"

for agent_dir in agents/*/; do
    agent=$(basename "$agent_dir")
    if [ -f "$agent_dir/"*.md ]; then
        echo "  ✓ $agent: working"
    else
        echo "  ⚠ $agent: NO OUTPUT - need task"
    fi
done

# 2. GIT AUTO-COMMIT
echo "[$DATE] Git sync..." >> "$LOG_FILE"
git add . 2>/dev/null

if ! git diff --cached --quiet; then
    git commit -m "chore: auto-sync $DATE" 2>/dev/null
    echo "[$DATE] ✓ Changes committed" >> "$LOG_FILE"
else
    echo "[$DATE] - No changes" >> "$LOG_FILE"
fi

# 3. UPDATE TASKS IF NEEDED
if [ -f TASKS_ACTIVE.md ]; then
    # Check if any task is stale (>1 hour old)
    last_update=$(stat -c %Y TASKS_ACTIVE.md 2>/dev/null || echo 0)
    now=$(date +%s)
    diff=$((now - last_update))
    
    if [ $diff -gt 3600 ]; then
        echo "[$DATE] ⚠ TASKS_ACTIVE.md stale (>1h), needs review" >> "$LOG_FILE"
    fi
fi

# 4. GENERATE NEXT TASKS (Perpetual Motion)
cat >> "$PROJECT_DIR/caesar_monitor.log" << 'NEXTTASKS'

--- NEXT CYCLE TASKS GENERATED ---
NEXTTASKS

echo "[$DATE] === CAESAR MONITOR COMPLETE ===" >> "$LOG_FILE"
