#!/bin/bash
# ============================================================
# AI DEPARTMENT — STARTUP SCRIPT
# ============================================================

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║          AI DEPARTMENT — RUSTORE LAUNCH                    ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

PROJECT_DIR="/opt/ai-department/rustore-launch"
cd "$PROJECT_DIR"

echo "📁 Project: $PROJECT_DIR"
echo ""

# Check GitHub SSH key
echo "🔑 GitHub SSH Status:"
if ssh -o ConnectTimeout=3 -o StrictHostKeyChecking=no -i ~/.ssh/github_deploy github.com 2>&1 | grep -q "successfully authenticated"; then
    echo "   ✅ GitHub SSH настроен"
    echo "   🌐 Repo: git@github.com:greopablo/ai-avatar-studio.git"
else
    echo "   ⚠️  GitHub SSH не настроен"
    echo "   📝 Добавь публичный SSH ключ в GitHub settings"
    echo "   Key: $(cat ~/.ssh/github_deploy.pub 2>/dev/null || echo 'не найден')"
fi

echo ""
echo "📊 Status:"
echo "   Агенты: $(find agents -maxdepth 1 -type d | wc -l) активных"
echo "   Файлы: $(find . -name '*.md' -type f | wc -l) документов"

echo ""
echo "🚀 Quick commands:"
echo "   ./perpetual_motion.sh   — полный цикл + GitHub push"
echo "   ./local_sync.sh          — синхронизация локальная"
echo "   ./auto_commit.sh         — только коммит"
echo "   cat PROGRESS_REPORT.txt  — статус проекта"
echo ""

# Show last activity
if [ -f perpetual_motion.log ]; then
    echo "📜 Last activity:"
    tail -5 perpetual_motion.log
fi

echo ""
