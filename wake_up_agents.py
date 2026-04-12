#!/usr/bin/env python3
"""
AI DEPARTMENT CONTROLLER
========================
Script: wake_up_agents.py
Purpose: Monitor and wake up AI agents, report progress to Telegram

Usage: python3 wake_up_agents.py
Runs: Every 60 seconds (infinite loop)
"""

import os
import time
import json
import subprocess
from datetime import datetime
from pathlib import Path

# Configuration
VPS_HOST = "45.159.189.85"
VPS_USER = "vps"
VPS_PASS = "0N#eq2F0EHg4w-"
PROJECT_PATH = "/opt/ai-department/rustore-launch"

# Telegram (placeholder - user needs to add their bot token and chat ID)
TELEGRAM_BOT_TOKEN = ""  # Add your bot token
TELEGRAM_CHAT_ID = ""    # Add your chat ID

# Agent definitions with their expected deliverables
AGENTS = {
    "daniel": {
        "role": "CEO / Orchestrator",
        "files": ["strategy.md"],
        "weight": 10,  # 10% of total
        "last_task": "Coordinate sprint 2"
    },
    "sophia": {
        "role": "Product",
        "files": ["product_design.md", "design/"],
        "weight": 15,
        "last_task": "UI components implementation"
    },
    "ethan": {
        "role": "Tech Lead",
        "files": ["architecture.md", "flutter/"],
        "weight": 20,
        "last_task": "Backend API endpoints"
    },
    "ava": {
        "role": "Growth",
        "files": ["growth_strategy.md"],
        "weight": 10,
        "last_task": "Marketing assets"
    },
    "alexander": {
        "role": "BizDev",
        "files": ["bizdev.md"],
        "weight": 10,
        "last_task": "Partner outreach"
    },
    "isabella": {
        "role": "Monetization",
        "files": ["monetization.md"],
        "weight": 10,
        "last_task": "Payment integration"
    },
    "michael": {
        "role": "Anti-Fraud",
        "files": ["security.md", "backend/"],
        "weight": 10,
        "last_task": "Security implementation"
    },
    "emma": {
        "role": "QA",
        "files": ["qa_plan.md", "tests/"],
        "weight": 10,
        "last_task": "Test automation"
    },
    "caesar": {
        "role": "Controller",
        "files": ["TASKS_ACTIVE.md", "PROGRESS_REPORT.txt"],
        "weight": 5,
        "last_task": "Monitor and report"
    }
}

def log(msg):
    """Log with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")
    with open("/opt/ai-department/controller.log", "a") as f:
        f.write(f"[{timestamp}] {msg}\n")

def send_telegram(message):
    """Send message to Telegram"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        log(f"Telegram not configured. Message: {message}")
        return False
    
    try:
        import urllib.request
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = urllib.parse.urlencode({
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }).encode()
        
        req = urllib.request.Request(url, data=data)
        urllib.request.urlopen(req, timeout=10)
        log(f"Telegram sent: {message[:50]}...")
        return True
    except Exception as e:
        log(f"Telegram error: {e}")
        return False

def ssh_connect():
    """Connect to VPS"""
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(VPS_HOST, port=22, username=VPS_USER, password=VPS_PASS, timeout=10)
        return client
    except Exception as e:
        log(f"SSH connection failed: {e}")
        return None

def check_agent_progress(client, agent_name, agent_info):
    """Check if agent is making progress"""
    try:
        # Check for recent commits from this agent
        cmd = f'"'"'cd {PROJECT_PATH} && git log --author="{agent_name}" --oneline -1 2>/dev/null | head -1'"'"'
        stdin, stdout, stderr = client.exec_command(cmd)
        last_commit = stdout.read().decode().strip()
        
        # Check if agent has recent changes
        agent_dir = f"{PROJECT_PATH}/agents/{agent_name}"
        stdin, stdout, stderr = client.exec_command(f'"'"'ls -la {agent_dir}/ 2>/dev/null | wc -l'"'"')
        file_count = int(stdout.read().decode().strip())
        
        return {
            "name": agent_name,
            "role": agent_info["role"],
            "files_exist": file_count > 2,
            "last_commit": last_commit,
            "task": agent_info["last_task"]
        }
    except:
        return None

def calculate_overall_progress(agent_statuses):
    """Calculate overall project progress"""
    # Base progress from sprint 1 completion
    base_progress = 25  # Sprint 1 done
    
    # Additional progress based on files created
    files_progress = 0
    for status in agent_statuses:
        if status and status["files_exist"]:
            weight = AGENTS.get(status["name"], {}).get("weight", 0)
            files_progress += weight * 0.3  # 30% weight for having files
    
    # Check for recent commits
    commit_progress = 0
    for status in agent_statuses:
        if status and status["last_commit"]:
            weight = AGENTS.get(status["name"], {}).get("weight", 0)
            commit_progress += weight * 0.5  # 50% weight for active commits
    
    total = min(100, base_progress + files_progress + commit_progress)
    return int(total)

def get_active_tasks(client):
    """Get currently active tasks from TASKS_ACTIVE.md"""
    try:
        stdin, stdout, stderr = client.exec_command(f'"'"'cat {PROJECT_PATH}/TASKS_ACTIVE.md 2>/dev/null | grep -E "^\[ \]" | head -5'"'"')
        tasks = stdout.read().decode().strip().split("\n")
        return [t for t in tasks if t][:3]
    except:
        return []

def wake_up_agent(client, agent_name):
    """Wake up a sleeping agent"""
    log(f"WAKING UP: {agent_name}")
    
    # Create a task file for the agent
    task_content = f"""
# TASK FOR {agent_name.upper()}
Generated: {datetime.now().strftime('"'"'%Y-%m-%d %H:%M'"'"')}
Status: WAITING FOR ACTION

TASK: Continue development. Check TASKS_ACTIVE.md for current tasks.
If no files created - create them now.
"""
    
    agent_dir = f"{PROJECT_PATH}/agents/{agent_name}"
    cmd = f'"'"'echo \'"'"'{task_content}\'"'"' > {agent_dir}/WAKE_UP_TASK.md'"'"'
    client.exec_command(cmd)
    
    return f"Task created for {agent_name}"

def main():
    """Main controller loop"""
    log("=" * 60)
    log("AI DEPARTMENT CONTROLLER STARTED")
    log("=" * 60)
    
    last_progress = 0
    last_status = {}
    
    while True:
        try:
            log("Checking AI Department status...")
            
            client = ssh_connect()
            if not client:
                log("Cannot connect to VPS. Retrying in 60s...")
                time.sleep(60)
                continue
            
            # Check each agent
            agent_statuses = []
            sleeping_agents = []
            
            for agent_name, agent_info in AGENTS.items():
                status = check_agent_progress(client, agent_name, agent_info)
                if status:
                    agent_statuses.append(status)
                    if not status["files_exist"] and not status["last_commit"]:
                        sleeping_agents.append(agent_name)
            
            # Calculate progress
            current_progress = calculate_overall_progress(agent_statuses)
            
            # Get active tasks
            active_tasks = get_active_tasks(client)
            
            # Report if progress changed
            if current_progress != last_progress:
                log(f"PROGRESS CHANGED: {last_progress}% -> {current_progress}%")
                
                # Build status message
                active_agents = [s["name"] for s in agent_statuses if s["files_exist"]]
                doing_tasks = [s["task"] for s in agent_statuses if s["files_exist"]][:3]
                
                status_msg = f"""🚀 <b>AI Department Progress</b>

📊 Progress: <b>{current_progress}%</b> (was {last_progress}%)

👥 Active: {'"'"', '"'"'.join(active_agents[:5]) if active_agents else '"'"'None'"'"'}

📋 Now: {doing_tasks[0] if doing_tasks else '"'"'Checking...'"'"'}

⏰ {datetime.now().strftime('"'"'%H:%M'"'"')}"""
                
                send_telegram(status_msg)
                
                # Wake up sleeping agents
                for agent in sleeping_agents:
                    wake_up_agent(client, agent)
                    send_telegram(f"⚠️ {agent.upper()} was sleeping - task assigned!")
                
                last_progress = current_progress
            
            # If no progress for 5+ minutes, poke everyone
            if current_progress == last_progress and last_status == agent_statuses:
                log("No progress detected. Sending reminder...")
                reminder_msg = f"""🔔 <b>Reminder</b>

Project at {current_progress}%

{sleeping_agents[0].upper() if sleeping_agents else '"'"'All'"'"'} - continue work!

Next check in 1 minute."""
                # send_telegram(reminder_msg)
            
            last_status = agent_statuses
            
            # Update TASKS_ACTIVE.md with last check
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            update = f"""
## Controller Check: {timestamp}
Progress: {current_progress}%
Active agents: {len([s for s in agent_statuses if s and s['"'"'files_exist'"'"']])}/9
"""
            client.exec_command(f'"'"'echo "{update}" >> {PROJECT_PATH}/TASKS_ACTIVE.md'"'"')
            
            client.close()
            
            log(f"Check complete. Progress: {current_progress}%. Next in 60s...")
            
        except Exception as e:
            log(f"Error in main loop: {e}")
        
        time.sleep(60)  # Check every 60 seconds

if __name__ == "__main__":
    main()

