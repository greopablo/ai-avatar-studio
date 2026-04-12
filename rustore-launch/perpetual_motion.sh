#!/bin/bash
# ============================================================
# AI DEPARTMENT — PERPETUAL MOTION SYSTEM
# Система бесконечного цикла работы без остановок
# Автор: Caesar (Контролер)
# ============================================================

PROJECT_DIR="/opt/ai-department/rustore-launch"
GITHUB_REMOTE="git@github.com:greopablo/ai-avatar-studio.git"
LOG_FILE="$PROJECT_DIR/perpetual_motion.log"
STATUS_FILE="$PROJECT_dir/.perpetual_status"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

log() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# ============================================================
# 1. CHECK GITHUB CONNECTIVITY
# ============================================================
check_github() {
    log "${YELLOW}Проверка GitHub...${NC}"
    
    # Test SSH connection
    if ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no -i ~/.ssh/github_deploy github.com 2>&1 | grep -q "You've successfully authenticated"; then
        log "${GREEN}✅ GitHub SSH подключение OK${NC}"
        return 0
    else
        log "${RED}⚠️ GitHub SSH недоступен${NC}"
        return 1
    fi
}

# ============================================================
# 2. ENSURE GITHUB REMOTE EXISTS
# ============================================================
setup_remote() {
    cd "$PROJECT_DIR" || exit 1
    
    # Check if remote exists
    if git remote get-url origin 2>/dev/null | grep -q "github.com"; then
        log "Remote origin уже настроен"
    else
        log "Настраиваю remote origin..."
        git remote add origin "$GITHUB_REMOTE" 2>/dev/null ||         git remote set-url origin "$GITHUB_REMOTE"
        
        # Configure branch
        git branch -M main 2>/dev/null || git branch -M master
        
        log "${GREEN}✅ Remote настроен${NC}"
    fi
}

# ============================================================
# 3. AUTO-COMMIT ALL CHANGES
# ============================================================
auto_commit() {
    cd "$PROJECT_DIR" || exit 1
    
    # Add all changes
    git add -A 2>/dev/null
    
    # Check for changes
    if git diff --cached --quiet; then
        log "Нет изменений для коммита"
        return 0
    fi
    
    # Get list of changed files
    changed_files=$(git diff --cached --name-only | wc -l)
    
    # Create commit
    commit_msg="chore: auto-sync $(date '+%Y-%m-%d %H:%M')

Auto-generated commit by Perpetual Motion System
Changed files: $changed_files

[skip-ci]"
    
    if git commit -m "$commit_msg"; then
        log "${GREEN}✅ ЗаКоммичены изменения ($changed_files файлов)${NC}"
        return 1  # Has changes
    else
        log "${RED}❌ Ошибка коммита${NC}"
        return 0
    fi
}

# ============================================================
# 4. PUSH TO GITHUB
# ============================================================
push_to_github() {
    cd "$PROJECT_DIR" || exit 1
    
    # Check if there are commits to push
    if ! git rev-parse HEAD@{u} 2>/dev/null; then
        # First push - set upstream
        log "Первый push на GitHub..."
        GIT_SSH_COMMAND="ssh -i ~/.ssh/github_deploy" git push -u origin main 2>&1 | tee -a "$LOG_FILE"
    else
        # Regular push
        log "Push на GitHub..."
        GIT_SSH_COMMAND="ssh -i ~/.ssh/github_deploy" git push origin main 2>&1 | tee -a "$LOG_FILE"
    fi
    
    if [ $? -eq 0 ]; then
        log "${GREEN}✅ Push на GitHub успешен${NC}"
        return 0
    else
        log "${RED}❌ Ошибка push${NC}"
        return 1
    fi
}

# ============================================================
# 5. CHECK AGENTS STATUS
# ============================================================
check_agents() {
    log "${YELLOW}Проверка статуса агентов...${NC}"
    
    agents=("daniel" "sophia" "ethan" "ava" "alexander" "isabella" "michael" "emma" "caesar")
    all_done=true
    
    for agent in "${agents[@]}"; do
        agent_dir="$PROJECT_DIR/agents/$agent"
        
        if [ -d "$agent_dir" ]; then
            files=$(find "$agent_dir" -name "*.md" -type f 2>/dev/null | wc -l)
            if [ "$files" -gt 0 ]; then
                log "  ✅ $agent: $files файлов"
            else
                log "  ⚠️  $agent: нет файлов (нужна задача)"
                all_done=false
            fi
        else
            log "  🔴 $agent: папка не существует"
            mkdir -p "$agent_dir"
            all_done=false
        fi
    done
    
    if $all_done; then
        log "${GREEN}✅ Все агенты активны${NC}"
    else
        log "${YELLOW}⚠️ Некоторые агенты нуждаются в задачах${NC}"
    fi
}

# ============================================================
# 6. GENERATE TASKS FOR IDLE AGENTS
# ============================================================
generate_tasks() {
    log "${YELLOW}Проверка задач...${NC}"
    
    # Read current tasks
    if [ -f "$PROJECT_DIR/TASKS_ACTIVE.md" ]; then
        last_task_update=$(stat -c %Y "$PROJECT_DIR/TASKS_ACTIVE.md" 2>/dev/null || echo 0)
        now=$(date +%s)
        diff=$((now - last_task_update))
        
        # If tasks file is older than 1 hour, update it
        if [ $diff -gt 3600 ]; then
            log "TASKS_ACTIVE.md устарел, обновляю..."
            
            # Add next phase tasks
            cat >> "$PROJECT_DIR/TASKS_ACTIVE.md" << 'TASKS'

---

## 🔄 АВТООБНОВЛЕНО: $(date '+%Y-%m-%d %H:%M')

### Следующие задачи для непрерывного цикла:

#### Implementation Sprint 1:
- [ ] Настроить Flutter проект
- [ ] Реализовать Auth модуль
- [ ] Интегрировать Kandinsky API
- [ ] Создать базовый UI

#### Testing:
- [ ] Написать unit тесты
- [ ] UI smoke tests
- [ ] API integration tests

#### Documentation:
- [ ] API documentation (OpenAPI)
- [ ] Developer guide
- [ ] Deployment guide

TASKS
            
            log "${GREEN}✅ Задачи обновлены${NC}"
        fi
    fi
}

# ============================================================
# 7. UPDATE PROGRESS REPORT
# ============================================================
update_progress() {
    log "${YELLOW}Обновляю прогресс...${NC}"
    
    # Update timestamp in progress file
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Add activity log entry
    activity="
$(date '+%Y-%m-%d %H:%M') | 🔄 Perpetual Motion System: sync complete"
    
    if [ -f "$PROJECT_DIR/PROGRESS_REPORT.txt" ]; then
        # Update last modified timestamp
        sed -i "s/Последнее обновление:.*/Последнее обновление: $timestamp UTC/" "$PROJECT_DIR/PROGRESS_REPORT.txt" 2>/dev/null
        log "Progress report обновлён"
    fi
}

# ============================================================
# 8. HEALTH CHECK
# ============================================================
health_check() {
    log "${YELLOW}Health check...${NC}"
    
    # Check disk space
    disk_usage=$(df -h / | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ "$disk_usage" -gt 90 ]; then
        log "${RED}⚠️ ВНИМАНИЕ: Диск заполнен на $disk_usage%${NC}"
    else
        log "Disk usage: $disk_usage% OK"
    fi
    
    # Check memory
    mem_available=$(free -m | grep Mem | awk '{print $7}')
    if [ "$mem_available" -lt 500 ]; then
        log "${YELLOW}⚠️ Мало свободной памяти: ${mem_available}MB${NC}"
    else
        log "Memory available: ${mem_available}MB OK"
    fi
    
    # Check git status
    cd "$PROJECT_DIR"
    uncommitted=$(git status --porcelain | wc -l)
    log "Незакоммиченных файлов: $uncommitted"
}

# ============================================================
# MAIN LOOP
# ============================================================
main() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║     AI DEPARTMENT — PERPETUAL MOTION SYSTEM               ║"
    echo "║     $(date '+%Y-%m-%d %H:%M:%S')                         ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    
    log "=========================================="
    log "PERPETUAL MOTION CYCLE START"
    log "=========================================="
    
    # Run all checks
    check_agents
    generate_tasks
    update_progress
    health_check
    
    # Git operations
    setup_remote
    auto_commit
    
    # Push to GitHub (if available)
    if check_github; then
        push_to_github
    else
        log "⚠️ GitHub недоступен, пропускаем push"
        log "Добавь SSH ключ в GitHub для синхронизации"
    fi
    
    log "=========================================="
    log "PERPETUAL MOTION CYCLE COMPLETE"
    log "=========================================="
    echo ""
}

# Run
main

# Exit with success
exit 0
