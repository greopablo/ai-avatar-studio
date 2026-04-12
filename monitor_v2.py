#!/usr/bin/env python3
import os, json, subprocess, time
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

AGENTS = {
    'ethan': 'Backend API / core logic',
    'sophia': 'Flutter screens / UI logic',
    'michael': 'DB models / security code',
    'isabella': 'payment service',
    'emma': 'tests / ci checks',
    'alexander': 'go-to-market artifacts',
    'ava': 'growth mechanics',
    'daniel': 'orchestration / priorities',
    'caesar': 'control loop',
}

FEATURE_PREFIXES = ('feat:', 'fix:', 'refactor:', 'perf:', 'test:')
CODE_EXTS = ('.py', '.dart', '.yaml', '.yml', '.toml', '.sql')


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
        'last_head': '',
        'last_feature_commit_ts': 0,
        'last_code_change_ts': 0,
        'last_wake_ts': 0,
        'last_report_ts': 0,
    }


def save_state(s):
    STATE.write_text(json.dumps(s, ensure_ascii=False, indent=2), encoding='utf-8')


def git_sync():
    sh('git add -A')
    rc, out, err = sh('git diff --cached --quiet')
    committed = False
    if rc != 0:
        msg = datetime.now(timezone.utc).strftime('chore: auto-sync %Y-%m-%d %H:%M UTC')
        sh(f'git commit -m "{msg}"')
        committed = True
    sh('GIT_SSH_COMMAND="ssh -i ~/.ssh/github_deploy" git push origin main')
    rc, head, _ = sh('git rev-parse HEAD')
    return head if rc == 0 else '', committed


def last_feature_commit_time():
    rc, out, _ = sh("git log --since='72 hours ago' --pretty=format:'%ct|%s' -n 200")
    if rc != 0 or not out:
        return 0
    best = 0
    for line in out.splitlines():
        try:
            ts_s, subj = line.split('|', 1)
            ts = int(ts_s)
            if subj.lower().startswith(FEATURE_PREFIXES):
                best = max(best, ts)
        except Exception:
            pass
    return best


def code_stats():
    # count code files + total lines in implementation
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


def progress_percent():
    # Weighted practical maturity score (simple, deterministic)
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
    if fc >= 20: score += 4
    if lc >= 1000: score += 4
    return min(100, score), fc, lc


def wake_cycle(reason):
    now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    lines = [
        f"\n## WAKE CYCLE {now}",
        f"Причина: {reason}",
        "Только РЕАЛЬНЫЙ КОД (.py/.dart), без пустой документации.",
    ]
    for a, task in AGENTS.items():
        p = PROJ / 'agents' / a
        p.mkdir(parents=True, exist_ok=True)
        (p / 'WAKE_TASK.txt').write_text(
            f"[{now}] WAKE UP: {task}. Сразу код + commit + push.\n", encoding='utf-8'
        )
        lines.append(f"- {a}: {task}")
    with TASKS.open('a', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')


def single_instance():
    LOCK.parent.mkdir(parents=True, exist_ok=True)
    if LOCK.exists():
        try:
            pid = int(LOCK.read_text().strip())
            os.kill(pid, 0)
            return False
        except Exception:
            pass
    LOCK.write_text(str(os.getpid()))
    return True


def main():
    if not single_instance():
        return
    try:
        st = load_state()
        now = int(time.time())

        head, committed = git_sync()
        feat_ts = last_feature_commit_time()
        pct, code_files, code_lines = progress_percent()

        # Detect stagnation: no feature commits 15 min OR no HEAD change 10 min
        stale_feature = (now - feat_ts) > 900 if feat_ts else True
        stale_head = (head == st.get('last_head'))

        if stale_feature and (now - st.get('last_wake_ts', 0) > 600):
            wake_cycle('нет feature/fix/refactor/perf/test коммитов > 15 минут')
            st['last_wake_ts'] = now
            tg("⚠️ Пинок отдела: нет feature-коммитов >15 мин. Раздал WAKE_TASK всем.")
            log('Wake cycle triggered (feature stale)')

        # Re-sync after possible wake task writes
        head2, _ = git_sync()
        if head2:
            head = head2

        # Report on each percent change
        if pct != st.get('last_percent', -1):
            active_now = []
            for a in AGENTS:
                rc, out, _ = sh(f"git log --since='30 minutes ago' --pretty=format:'%s' -- agents/{a} implementation | head -n 1")
                if out:
                    active_now.append(f"{a}")
            active_text = ', '.join(active_now[:5]) if active_now else 'нет явной активности'
            msg = f"Хозяин — теперь {pct}%\nСейчас работают: {active_text}\nКод: {code_files} файлов / {code_lines} строк"
            tg(msg)
            log(f'Percent changed: {st.get("last_percent")} -> {pct}')
            st['last_percent'] = pct

        st['last_head'] = head
        st['last_feature_commit_ts'] = feat_ts
        save_state(st)
        log(f'OK: pct={pct}, head={head[:8] if head else "none"}, code_files={code_files}')

    finally:
        try:
            LOCK.unlink(missing_ok=True)
        except Exception:
            pass

if __name__ == '__main__':
    main()
