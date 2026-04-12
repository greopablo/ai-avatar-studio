#!/usr/bin/env python3
import json, time, subprocess
from datetime import datetime, timezone
from pathlib import Path
from urllib import request, parse

ROOT = Path('/opt/ai-department')
PROJ = Path('/opt/ai-department/rustore-launch')
STATE = ROOT / 'monitor_state.json'
LOCK = ROOT / 'monitor.lock'
LOG = ROOT / 'monitor_v2.log'
TASKS = PROJ / 'TASKS_ACTIVE.md'

TOKEN = '8241576028:AAH-3YOXl2QocTOklIUBipy483QF3AqdWXU'
CHAT_ID = '2012881095'

# Последовательность активации (кто должен работать следующим)
SEQUENCE = [
    ('ethan', 'Backend API endpoints и бизнес-логика'),
    ('sophia', 'Flutter экраны и UX-флоу'),
    ('michael', 'DB модели и security checks'),
    ('isabella', 'Payment flow / подписки'),
    ('emma', 'Тесты и CI checks'),
    ('alexander', 'Rustore launch assets'),
    ('ava', 'Growth-механики и viral hooks'),
    ('daniel', 'Оркестрация/приоритизация задач'),
]

CODE_EXTS = ('.py', '.dart', '.yaml', '.yml', '.toml', '.sql')
FEATURE_PREFIXES = ('feat:', 'fix:', 'refactor:', 'perf:', 'test:')


def log(msg):
    ts = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    line = f'[{ts}] {msg}'
    print(line)
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open('a', encoding='utf-8') as f:
        f.write(line + '\n')


def sh(cmd, cwd=PROJ):
    p = subprocess.run(cmd, cwd=str(cwd), shell=True, text=True, capture_output=True)
    return p.returncode, p.stdout.strip(), p.stderr.strip()


def tg(text):
    try:
        data = parse.urlencode({'chat_id': CHAT_ID, 'text': text}).encode()
        req = request.Request(f'https://api.telegram.org/bot{TOKEN}/sendMessage', data=data)
        request.urlopen(req, timeout=15)
        return True
    except Exception as e:
        log(f'Telegram error: {e}')
        return False


def load_state():
    if STATE.exists():
        return json.loads(STATE.read_text(encoding='utf-8'))
    return {
        'last_percent': -1,
        'last_remote_head': '',
        'last_remote_change_ts': 0,
        'seq_index': 0,
    }


def save_state(s):
    STATE.write_text(json.dumps(s, ensure_ascii=False, indent=2), encoding='utf-8')


def ensure_push_and_fetch():
    # Коммит/пуш локальных изменений
    sh('git add -A')
    rc, _, _ = sh('git diff --cached --quiet')
    if rc != 0:
        msg = datetime.now(timezone.utc).strftime('chore: auto-sync %Y-%m-%d %H:%M UTC')
        sh(f'git commit -m "{msg}"')
    sh('GIT_SSH_COMMAND="ssh -i ~/.ssh/github_deploy" git push origin main')

    # Обновляем remote refs и берем фактический head GitHub
    sh('GIT_SSH_COMMAND="ssh -i ~/.ssh/github_deploy" git fetch origin main --quiet')
    rc1, remote_head, _ = sh('git rev-parse origin/main')
    rc2, remote_ts, _ = sh('git show -s --format=%ct origin/main')
    rc3, remote_subject, _ = sh('git show -s --format=%s origin/main')
    if rc1 != 0:
        remote_head = ''
    if rc2 != 0 or not remote_ts.isdigit():
        remote_ts_int = 0
    else:
        remote_ts_int = int(remote_ts)
    return remote_head, remote_ts_int, remote_subject


def code_stats():
    root = PROJ / 'implementation'
    file_count = 0
    line_count = 0
    if root.exists():
        for p in root.rglob('*'):
            if p.is_file() and p.suffix in CODE_EXTS:
                file_count += 1
                try:
                    line_count += sum(1 for _ in p.open('r', encoding='utf-8', errors='ignore'))
                except Exception:
                    pass
    return file_count, line_count


def feature_commit_recent_minutes(minutes=60):
    rc, out, _ = sh(f"git log --since='{minutes} minutes ago' --pretty=format:'%s'")
    if rc != 0 or not out:
        return 0
    c = 0
    for s in out.splitlines():
        if s.lower().startswith(FEATURE_PREFIXES):
            c += 1
    return c


def calc_progress():
    score = 0
    checks = [
        (PROJ/'implementation'/'flutter'/'lib'/'main.dart', 8),
        (PROJ/'implementation'/'flutter'/'lib'/'screens'/'auth_screen.dart', 6),
        (PROJ/'implementation'/'flutter'/'lib'/'screens'/'style_screen.dart', 6),
        (PROJ/'implementation'/'backend'/'app'/'main.py', 10),
        (PROJ/'implementation'/'backend'/'app'/'api'/'auth.py', 10),
        (PROJ/'implementation'/'backend'/'app'/'api'/'generate.py', 10),
        (PROJ/'implementation'/'backend'/'app'/'models'/'user.py', 8),
        (PROJ/'implementation'/'backend'/'app'/'models'/'avatar.py', 8),
        (PROJ/'implementation'/'backend'/'app'/'services'/'payment.py', 8),
        (PROJ/'implementation'/'ci'/'.github'/'workflows'/'ci.yml', 6),
        (PROJ/'implementation'/'backend'/'docker-compose.yml', 6),
        (PROJ/'implementation'/'backend'/'requirements.txt', 6),
        (PROJ/'PROGRESS_REPORT.txt', 4),
        (PROJ/'TASKS_ACTIVE.md', 4),
    ]
    for path, w in checks:
        if path.exists() and path.stat().st_size > 0:
            score += w

    fc, lc = code_stats()
    if fc >= 25: score += 4
    if lc >= 1500: score += 4
    if feature_commit_recent_minutes(120) >= 3: score += 2

    return min(100, score), fc, lc


def detect_active_workers():
    # кто реально менял код за последние 30 минут
    rc, out, _ = sh("git log --since='30 minutes ago' --name-only --pretty=format:'---%an' | sed '/^$/d'")
    active = []
    if rc == 0 and out:
        current_author = ''
        touched = set()
        for line in out.splitlines():
            if line.startswith('---'):
                current_author = line[3:].strip().lower()
                continue
            if line.endswith(CODE_EXTS):
                touched.add((current_author, line))
        mapping = {
            'ethan': 'ethan', 'sophia': 'sophia', 'michael': 'michael', 'isabella': 'isabella',
            'emma': 'emma', 'alexander': 'alexander', 'ava': 'ava', 'daniel': 'daniel', 'caesar': 'caesar'
        }
        for a,_ in touched:
            for k in mapping:
                if k in a:
                    active.append(mapping[k])
    # unique preserve order
    seen = set(); ordered = []
    for a in active:
        if a not in seen:
            seen.add(a); ordered.append(a)
    return ordered


def wake_next_agent(st, reason):
    idx = st.get('seq_index', 0) % len(SEQUENCE)
    agent, task = SEQUENCE[idx]
    ts = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')

    agent_dir = PROJ / 'agents' / agent
    agent_dir.mkdir(parents=True, exist_ok=True)
    wake_file = agent_dir / 'WAKE_TASK.txt'
    wake_file.write_text(
        f"[{ts}] Активация: {reason}\n"
        f"Ответственный: {agent}\n"
        f"Задача: {task}\n"
        "Требование: создать/обновить РЕАЛЬНЫЙ код (.py/.dart), сделать commit и push.\n",
        encoding='utf-8'
    )

    with TASKS.open('a', encoding='utf-8') as f:
        f.write(
            f"\n## WAKE {ts}\n"
            f"Причина: {reason}\n"
            f"Активирован: {agent}\n"
            f"Задача: {task}\n"
            "Критерий: новый commit в GitHub <= 5 минут.\n"
        )

    st['seq_index'] = (idx + 1) % len(SEQUENCE)
    return agent, task


def single_instance():
    LOCK.parent.mkdir(parents=True, exist_ok=True)
    if LOCK.exists():
        try:
            pid = int(LOCK.read_text().strip())
            import os
            os.kill(pid, 0)
            return False
        except Exception:
            pass
    LOCK.write_text(str(__import__('os').getpid()))
    return True


def main():
    if not single_instance():
        return
    try:
        st = load_state()
        now = int(time.time())

        remote_head, remote_ts, remote_subject = ensure_push_and_fetch()
        pct, code_files, code_lines = calc_progress()
        active = detect_active_workers()

        # обновляем last_remote_change_ts
        if remote_head and remote_head != st.get('last_remote_head'):
            st['last_remote_change_ts'] = now
            st['last_remote_head'] = remote_head

        # если 5 минут нет НОВОГО remote commit — активируем следующего по очереди
        last_change = st.get('last_remote_change_ts', 0)
        if last_change == 0 and remote_head:
            st['last_remote_change_ts'] = now
            last_change = now

        if now - last_change >= 300:
            agent, task = wake_next_agent(st, 'на GitHub нет нового коммита > 5 минут')
            log(f'Wake triggered: {agent} | {task}')
            # Без лишнего спама в TG: не отправляем отдельный wake-msg
            # reset timer to avoid every-minute same poke
            st['last_remote_change_ts'] = now
            # фиксируем wake-коммит
            ensure_push_and_fetch()

        # Telegram только при изменении процента
        if pct != st.get('last_percent', -1):
            last_commit_human = datetime.fromtimestamp(remote_ts, tz=timezone.utc).strftime('%H:%M UTC') if remote_ts else 'n/a'
            current_task = SEQUENCE[st.get('seq_index', 0) % len(SEQUENCE)][1]
            who = ', '.join(active[:4]) if active else 'назначенный по очереди исполнитель'
            msg = (
                f"Хозяин — теперь {pct}%\n"
                f"Сейчас работают: {who}\n"
                f"Текущая задача: {current_task}\n"
                f"Крайний commit на GitHub: {last_commit_human}\n"
                f"Код: {code_files} файлов / {code_lines} строк"
            )
            tg(msg)
            log(f'Percent changed: {st.get("last_percent")} -> {pct}')
            st['last_percent'] = pct

        save_state(st)
        log(f'OK pct={pct}, remote={remote_head[:8] if remote_head else "none"}, active={active[:4]}')

    finally:
        try:
            LOCK.unlink(missing_ok=True)
        except Exception:
            pass

if __name__ == '__main__':
    main()
