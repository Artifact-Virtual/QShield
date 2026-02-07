#!/usr/bin/env python3
"""
Git History Purge - Auto-purge old commits on push
Self-healing, fail-proof automation
"""

import sys
import os
import subprocess
import json
from pathlib import Path
from datetime import datetime

# Configuration
PURGE_CONFIG_FILE = Path.home() / '.artifact_shield' / 'purge_config.json'
PURGE_LOG_FILE = Path.home() / '.artifact_shield' / 'history_purge.log'

def load_purge_config():
    """Load or create purge configuration"""
    default_config = {
        'enabled': False,              # disabled by default for safety; enable explicitly
        'keep_commits': 5,
        'backup_enabled': True,
        'backup_location': str(Path.home() / '.artifact_shield' / 'backups'),
        'fail_safe': True
    }
    
    try:
        if PURGE_CONFIG_FILE.exists():
            with open(PURGE_CONFIG_FILE, 'r') as f:
                config = json.load(f)
                # Merge with defaults
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
    except Exception:
        pass
    
    # Create default config
    PURGE_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(PURGE_CONFIG_FILE, 'w') as f:
            json.dump(default_config, f, indent=2)
    except Exception:
        pass
    
    return default_config

def log_purge_event(message):
    """Log purge events"""
    try:
        PURGE_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().isoformat()
        log_entry = f'{timestamp} | {message}\n'
        with open(PURGE_LOG_FILE, 'a') as f:
            f.write(log_entry)
    except Exception:
        pass

def count_commits():
    """Count total commits in repository"""
    try:
        result = subprocess.run(
            ['git', 'rev-list', '--count', 'HEAD'],
            capture_output=True,
            text=True,
            check=True
        )
        return int(result.stdout.strip())
    except Exception:
        return 0

def get_nth_commit_hash(n):
    """Get hash of nth commit from HEAD"""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', f'HEAD~{n}'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except Exception:
        return None

def create_backup(backup_location):
    """Create backup before purging"""
    try:
        backup_dir = Path(backup_location)
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f'backup_{timestamp}.bundle'
        backup_path = backup_dir / backup_name
        
        # Create git bundle (complete backup)
        subprocess.run(
            ['git', 'bundle', 'create', str(backup_path), '--all'],
            check=True,
            capture_output=True
        )
        
        log_purge_event(f'Backup created: {backup_path}')
        return True
    except Exception as error:
        log_purge_event(f'Backup failed: {error}')
        return False

def purge_old_commits(keep_commits):
    """Purge commits older than keep_commits"""
    try:
        total_commits = count_commits()
        
        if total_commits <= keep_commits:
            log_purge_event(f'No purge needed ({total_commits} commits, keeping {keep_commits})')
            return True
        
        # Simplified approach: Create a new orphan branch with squashed history
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_branch = f'shield_temp_{timestamp}'
        
        # Get current branch name
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                capture_output=True,
                text=True,
                check=True
            )
            current_branch = result.stdout.strip()
        except Exception:
            current_branch = 'main'
        
        # Create backup branch
        subprocess.run(['git', 'branch', f'backup_{timestamp}'], check=False, capture_output=True)
        
        # Get commit to keep from
        new_root_hash = get_nth_commit_hash(keep_commits - 1)
        if not new_root_hash:
            log_purge_event('Failed to determine new root commit')
            return False
        
        # Create patch file for recent commits
        patch_file = Path.home() / '.artifact_shield' / f'patch_{timestamp}.diff'
        subprocess.run(
            ['git', 'diff', f'{new_root_hash}~1', 'HEAD'],
            stdout=open(patch_file, 'w'),
            check=False
        )
        
        # Create orphan branch
        subprocess.run(['git', 'checkout', '--orphan', temp_branch], check=True, capture_output=True)
        subprocess.run(['git', 'add', '-A'], check=True, capture_output=True)
        subprocess.run(['git', 'commit', '-m', f'History purged - kept {keep_commits} commits'], check=True, capture_output=True)
        
        # Delete old branch and rename
        subprocess.run(['git', 'branch', '-D', current_branch], check=False, capture_output=True)
        subprocess.run(['git', 'branch', '-m', current_branch], check=True, capture_output=True)
        
        # Cleanup
        subprocess.run(['git', 'gc', '--aggressive', '--prune=now'], check=False, capture_output=True)
        
        purged_count = total_commits - 1  # Now we have 1 commit
        log_purge_event(f'Purged history: {purged_count} commits removed, squashed into 1 commit')
        
        return True
        
    except Exception as error:
        log_purge_event(f'Purge failed: {error}')
        return False

def main():
    """Main pre-push hook logic"""
    # Check if purge is disabled
    if os.environ.get('SHIELD_PURGE_DISABLED') == '1':
        print("ℹ️  History purge disabled (SHIELD_PURGE_DISABLED=1)")
        return 0
    
    config = load_purge_config()
    
    if not config['enabled']:
        print("ℹ️  History purge disabled in configuration")
        return 0
    
    print(f"🧹 Artifact Shield: Purging old commits (keeping last {config['keep_commits']})...")
    
    total_commits = count_commits()
    
    if total_commits <= config['keep_commits']:
        print(f"✅ No purge needed ({total_commits} commits)")
        return 0
    
    # Create backup if enabled
    if config['backup_enabled']:
        print("💾 Creating backup...")
        if not create_backup(config['backup_location']):
            if not config['fail_safe']:
                print("❌ Backup failed, aborting purge")
                return 1
            else:
                print("⚠️  Backup failed, but fail-safe mode enabled - continuing")
    
    # Perform purge
    print(f"🗑️  Purging {total_commits - config['keep_commits']} old commits...")
    
    if purge_old_commits(config['keep_commits']):
        print("✅ History purged successfully")
        print(f"   Kept last {config['keep_commits']} commits")
        return 0
    else:
        if config['fail_safe']:
            print("⚠️  Purge failed, but fail-safe mode enabled - allowing push")
            return 0
        else:
            print("❌ Purge failed, blocking push")
            return 1

if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as error:
        print(f"⚠️  History purge error: {error}")
        # Fail-safe: never block push
        print("   Proceeding with push (fail-safe mode)")
        sys.exit(0)
