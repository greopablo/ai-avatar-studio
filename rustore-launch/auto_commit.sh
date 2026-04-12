#!/bin/bash
# Auto-commit для AI Department
# Добавляет все изменения и коммитит

PROJECT_DIR="/opt/ai-department/rustore-launch"
cd "$PROJECT_DIR"

# Добавляем всё
git add .

# Проверяем есть ли изменения
if git diff --cached --quiet; then
    echo "[2026-04-12 19:33:18] Нет изменений для коммита"
else
    # Коммитим
    git commit -m "chore: auto-sync 2026-04-12 19:33
    
    [skip-ci]"
    echo "[2026-04-12 19:33:18] ✅ Изменения закоммичены"
fi
