#!/usr/bin/env python3
"""
AI DEPARTMENT CONTROLLER
Purpose: Monitor agents, wake them up, report to Telegram
Runs: Every 60 seconds
"""

import os, time, subprocess
from datetime import datetime

VPS_HOST = "45.159.189.85"
VPS_USER = "vps"
VPS_PASS = "0N#eq2F0EHg4w-"
PROJECT = "/opt/ai-department/rustore-launch"

# Telegram - SET YOUR VALUES!
BOT_TOKEN = "8241576028:AAH-3YOXl2QocTOklIUBipy483QF3AqdWXU"  # Your bot token
CHAT_ID = "2012881095"    # Your chat ID

AGENTS = {
    "daniel": {"role": "CEO", "task": "Sprint coordination"},
    "sophia": {"role": "Product", "task": "UI components"},
    "ethan": {"role": "Tech", "task": "Backend API"},
    "ava": {"role": "Growth", "task": "Marketing"},
    "alexander": {"role": "BizDev", "task": "Partners"},
    "isabella": {"role": "Money", "task": "Payments"},
    "michael": {"role": "Security", "task": "Anti-fraud"},
    "emma": {"role": "QA", "task": "Testing"},
    "caesar": {"role": "Controller", "task": "Monitoring"},
}

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print("[{}] {}".format(ts, msg))

def ssh_cmd(cmd_str):
    script = "sshpass -p '{}' ssh -o StrictHostKeyChecking=no {}@{} '{}'".format(
        VPS_PASS, VPS_USER, VPS_HOST, cmd_str
    )
    try:
        r = subprocess.run(script, shell=True, capture_output=True, text=True, timeout=30)
        return r.stdout.strip(), r.stderr.strip()
    except Exception as e:
        log("SSH error: {}".format(e))
        return "", ""

def telegram(msg):
    if not BOT_TOKEN or not CHAT_ID:
        log("TG: {}".format(msg[:50]))
        return
    try:
        import urllib.request, urllib.parse
        url = "https://api.telegram.org/bot{}/sendMessage".format(BOT_TOKEN)
        data = urllib.parse.urlencode({"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}).encode()
        urllib.request.urlopen(url, data=data, timeout=10)
        log("Telegram sent!")
    except Exception as e:
        log("TG error: {}".format(e))

def check_agents():
    results = {}
    for agent in AGENTS:
        agent_dir = PROJECT + "/agents/" + agent
        out, _ = ssh_cmd("ls -la " + agent_dir + "/ 2>/dev/null | grep -E '.md$' | wc -l")
        files = int(out) if out.isdigit() else 0
        
        out, _ = ssh_cmd("cd " + PROJECT + " && git log --author=" + agent + " --oneline -1 2>/dev/null")
        commit = out if out else None
        
        out, _ = ssh_cmd("cd " + PROJECT + " && git log --since='1 hour ago' --oneline | grep -c " + agent + " 2>/dev/null || echo 0")
        recent = int(out) if out.isdigit() else 0
        
        results[agent] = {
            "role": AGENTS[agent]["role"],
            "task": AGENTS[agent]["task"],
            "files": files,
            "commit": commit,
            "recent": recent,
            "active": files > 0 or recent > 0
        }
    return results

def calc_progress(results):
    base = 25
    file_bonus = sum(5 for r in results.values() if r["files"] > 0)
    commit_bonus = sum(10 for r in results.values() if r["recent"] > 0)
    return min(100, base + file_bonus + commit_bonus)

def main():
    log("=" * 50)
    log("AI DEPARTMENT CONTROLLER STARTED")
    log("=" * 50)
    
    last_pct = 0
    last_sleeping = set()
    
    while True:
        try:
            log("Checking AI Department...")
            results = check_agents()
            pct = calc_progress(results)
            
            active = [a for a, r in results.items() if r["active"]]
            sleeping = [a for a, r in results.items() if not r["active"]]
            
            log("Progress: {}%, Active: {}/9".format(pct, len(active)))
            
            # Report progress change
            if pct != last_pct:
                log("PROGRESS CHANGED: {}% -> {}%".format(last_pct, pct))
                doing = [r["task"] for r in results.values() if r["active"]][:3]
                msg = "🚀 <b>AI Department</b>\n\n📊 Progress: <b>{}%</b>\n\n👥 Active: {}\n\n📋 Now: {}\n\n⏰ {}".format(
                    pct, 
                    ", ".join(active[:5]) or "None", 
                    doing[0] if doing else "Checking...",
                    datetime.now().strftime("%H:%M")
                )
                telegram(msg)
                last_pct = pct
            
            # Wake sleeping agents
            if sleeping and sleeping != last_sleeping:
                for a in sleeping[:2]:
                    log("WAKING UP: {}".format(a))
                    ssh_cmd("echo 'WAKE UP! Task: " + AGENTS[a]["task"] + "' > " + PROJECT + "/agents/" + a + "/WAKE_TASK.txt")
                    telegram("⚠️ <b>{}</b> was sleeping! Task: {}".format(a.upper(), AGENTS[a]["task"]))
                last_sleeping = set(sleeping)
            
            log("Sleeping: {}/9".format(len(sleeping)))
            log("Next check in 60s...")
            
        except Exception as e:
            log("Error: {}".format(e))
        
        time.sleep(60)

if __name__ == "__main__":
    main()
