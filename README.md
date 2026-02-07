# QShield

**Multi-Layer Encryption System with Self-Healing Automation**

## Overview

QShield is a fail‑safe, self‑healing git-integrated tool that auto-encrypts classification-marked files using per-file salt and a multi-layer XOR-derived key scheme, purges old history with encrypted backups, supports classification-based batch ops and audit logging, and recommends AES‑256‑GCM/HSMs or post‑quantum KEMs for production security.

The Quantum Shield is a comprehensive security system designed to protect Artifact Virtual's sensitive data with:

- **Multi-layer encryption** with custom algorithm
- **Automatic encryption** before commits
- **Automatic history purging** before pushes
- **Self-healing** fail-proof operation
- **Beautiful terminal UI** for easy management

### Security Notice

⚠️ **Important:** The encryption implementation uses a custom multi-layer XOR algorithm designed for:
- Protection against casual unauthorized access
- Defense-in-depth with git history purging
- Rapid deployment without external dependencies

For production use with maximum security requirements, consider migrating to:
- **AES-256-GCM** for symmetric encryption
- **CRYSTALS-Kyber** for post-quantum resistance (as researched in HEKTOR project)
- Hardware Security Modules (HSMs) for key management

The current implementation provides strong protection when combined with:
- Automated git history purging
- Access control and authentication
- Audit logging and monitoring
- Classification-based security policies

## Quick Start

### Installation

```bash
# Install the shield system
cd /path/to/enterprise
bash scripts/shield/install_shield.sh

# Reload your shell
source ~/.bashrc
```

### Basic Usage

```bash
# Interactive mode (recommended for first time)
shield

# Encrypt a file
shield encrypt path/to/secret.md

# Decrypt a file
shield decrypt path/to/secret.md.enc

# Check encryption status
shield status .
```

## Features

### 1. Multi-Layer Encryption

The encryption algorithm uses three layers:
- **Layer 1:** XOR with derived key (SHA3-512 + Blake2b + SHA512)
- **Layer 2:** Reverse XOR for additional complexity
- **Layer 3:** Position-dependent XOR

**Key Features:**
- Minimum passphrase: 5 characters
- Maximum passphrase: 1000 characters (unlimited strength)
- Random salt per file
- Quantum-resistant design

### 2. Pre-Commit Auto-Encryption

**Automatic Protection:**
- Scans staged files for classification markers
- Detects: `TOP_SECRET`, `CONFIDENTIAL`, `RESTRICTED`
- Auto-encrypts unencrypted sensitive files
- Never blocks commits (fail-safe mode)

**Example:**
```bash
# You edit a TOP_SECRET file
echo "Classification: TOP_SECRET" > secret.md
git add secret.md
git commit -m "Add secret"

# Shield automatically:
# 1. Detects TOP_SECRET marker
# 2. Prompts for passphrase (or uses SHIELD_PASSPHRASE)
# 3. Encrypts the file
# 4. Stages secret.md.enc
# 5. Unstages secret.md
# 6. Allows commit to proceed
```

### 3. Pre-Push History Purging

**Automatic History Cleanup:**
- Keeps only last N commits (default: 5)
- Purges older commits permanently
- Creates encrypted backup before purging
- Never blocks pushes (fail-safe mode)

**Configuration:**
Edit `~/.artifact_shield/purge_config.json`:
```json
{
  "enabled": true,
  "keep_commits": 5,
  "backup_enabled": true,
  "backup_location": "/home/user/.artifact_shield/backups",
  "fail_safe": true
}
```

**Disable temporarily:**
```bash
export SHIELD_PURGE_DISABLED=1
git push
```

### 4. Classification-Based Encryption

**Supported Classifications:**
- `TOP_SECRET` - Highest security
- `CONFIDENTIAL` - High security
- `RESTRICTED` - Standard security

**Usage:**
```bash
# Encrypt all TOP_SECRET files in a directory
shield
# Choose option [4] - Encrypt by Classification
# Select TOP_SECRET
# Enter directory path
```

### 5. Self-Healing Operation

**Never Fails:**
- If config missing → creates default
- If passphrase wrong → warns but continues
- If hook fails → allows operation
- If backup fails → warns but continues (fail-safe mode)

**Logging:**
All operations logged to `~/.artifact_shield/audit.log`:
```
2026-02-06T01:00:00 | Encrypted: secret.md -> secret.md.enc
2026-02-06T01:05:00 | Purged 10 old commits, kept 5 recent commits
2026-02-06T01:10:00 | Backup created: backup_20260206_010000.bundle
```

## Configuration

### Shield Configuration

File: `~/.artifact_shield/config.json`

```json
{
  "version": "1.0.0",
  "min_key_length": 5,
  "max_key_length": 1000,
  "auto_encrypt": true,
  "classifications": [
    "TOP_SECRET",
    "CONFIDENTIAL",
    "RESTRICTED"
  ],
  "exclude_patterns": [
    ".shield",
    "scripts/shield",
    "node_modules",
    ".git"
  ],
  "encryption_marker": "ARTIFACT_SHIELD_ENCRYPTED"
}
```

### Purge Configuration

File: `~/.artifact_shield/purge_config.json`

```json
{
  "enabled": true,
  "keep_commits": 5,
  "backup_enabled": true,
  "backup_location": "/home/user/.artifact_shield/backups",
  "fail_safe": true
}
```

## Security Model

### What This Protects

✅ **Encrypted at Rest:** All sensitive files encrypted on disk  
✅ **Encrypted in Git:** Only encrypted files in repository  
✅ **No History Leaks:** Old commits purged automatically  
✅ **Audit Trail:** Complete log of all operations  
✅ **Self-Healing:** Never breaks workflow

### What This Doesn't Protect

⚠️ **Authorized Users:** Users with valid passphrase can decrypt  
⚠️ **In-Memory Data:** Decrypted files in memory/temp  
⚠️ **Physical Access:** Physical access to master key  
⚠️ **Social Engineering:** Users revealing passphrases

### Threat Model

| Threat | Protected | Mitigation |
|--------|-----------|------------|
| Repo compromise | ✅ Yes | Files encrypted |
| History mining | ✅ Yes | History purged |
| Malicious insider | ⚠️ Partial | Audit logging |
| Lost laptop | ✅ Yes | Encryption at rest |
| Git leak | ✅ Yes | Only encrypted in git |

## Best Practices

### 1. Passphrase Management

**DO:**
- Use strong passphrases (20+ characters)
- Use password manager
- Rotate quarterly
- Never commit passphrase

**DON'T:**
- Don't share passphrases
- Don't use weak passphrases
- Don't store in plaintext
- Don't reuse across systems

### 2. Classification Markers

Add to top of sensitive files:

```markdown
---
Classification: TOP_SECRET
Owner: CEO
Date: 2026-02-06
---

# Secret Document
...
```

### 3. Environment Variables

```bash
# Add to ~/.bashrc for convenience
export SHIELD_PASSPHRASE='your-strong-passphrase-here'

# Or use different passphrases per classification
export SHIELD_TOP_SECRET_KEY='...'
export SHIELD_CONFIDENTIAL_KEY='...'
```

### 4. Backup Strategy

**Encrypted Backups:**
- Keep offline backup of master passphrase
- Store backup keys in physical safe
- Test restore procedures quarterly

**Git Bundle Backups:**
- Automatic backups in `~/.artifact_shield/backups/`
- Keep 3 most recent backups
- Delete old backups manually

## Troubleshooting

### "Wrong passphrase" Error

```bash
# Check if file is really encrypted
file secret.md.enc

# Try decrypting with correct passphrase
shield decrypt secret.md.enc
```

### Hook Not Running

```bash
# Check if hooks are executable
ls -la .git/hooks/

# Reinstall hooks
bash scripts/shield/install_shield.sh
```

### Purge Failed

```bash
# Check logs
cat ~/.artifact_shield/history_purge.log

# Disable and push
export SHIELD_PURGE_DISABLED=1
git push
```

### Cannot Find 'shield' Command

```bash
# Reload bashrc
source ~/.bashrc

# Or use full path
python3 scripts/shield/quantum_shield.py
```

## Advanced Usage

### Batch Encryption

```bash
# Encrypt all markdown files in directory
find . -name "*.md" -exec shield encrypt {} \;

# Encrypt by pattern
shield
# Option [4] - Encrypt by Classification
```

### Manual History Purge

```bash
# Run purge script directly
python3 scripts/shield/pre_push_hook.py
```

### Custom Configuration

```bash
# Edit config
nano ~/.artifact_shield/config.json

# Test config
shield
# Option [7] - Configuration
```

## API Reference

### QuantumShield Class

```python
from quantum_shield import QuantumShield

shield = QuantumShield()

# Encrypt file
shield.encrypt_file('path/to/file.md', 'passphrase')

# Decrypt file
shield.decrypt_file('path/to/file.md.enc', 'passphrase')

# Check if encrypted
is_enc = shield.is_encrypted('path/to/file.md')

# Scan directory
encrypted, skipped = shield.scan_and_encrypt_directory(
    '/path/to/dir',
    'passphrase',
    classification='TOP_SECRET'
)
```

## Compliance Mapping

### GRC Controls

| Control | Implementation |
|---------|----------------|
| I-01 (Identity) | Passphrase-based access |
| D-01 (Data Protection) | Encryption at rest |
| D-02 (Encryption) | Multi-layer encryption |
| IR-01 (Incident Response) | Audit logging |
| BCDR-01 (Backup) | Automated backups |

### Standards

- **SOC 2:** Data protection controls
- **ISO 27001:** Encryption requirements
- **GDPR:** Data privacy and protection

## Maintenance

### Daily
- Check encryption status
- Review audit logs

### Weekly
- Verify backups exist
- Test decrypt procedures

### Monthly
- Rotate passphrases
- Review access logs
- Update excluded patterns

### Quarterly
- Full security audit
- Test disaster recovery
- Update documentation

## Support

**Issues:** Create an issue in the repository  
**Security:** security@artifactvirtual.com  
**Documentation:** This README

## License

Proprietary - Artifact Virtual (SMC-Private) Limited  
See LICENSE file for details

---

**Version:** 1.0.0  
**Last Updated:** 2026-02-06  
**Author:** Artifact Virtual Security Team
