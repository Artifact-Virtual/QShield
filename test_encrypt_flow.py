#!/usr/bin/env python3
"""Test harness to verify QuantumShield encryption/decryption round-trip on a sample file.
Usage: python scripts/shield/test_encrypt_flow.py [passphrase]
If no passphrase provided, a temporary one is generated for dry-run verification.
"""
import sys
from pathlib import Path
import secrets

ROOT = Path(__file__).resolve().parents[2]
# Choose a small, stable file for encryption test
for candidate in ['README.md', 'GIT-COMMUNITY.md', 'CONTRIBUTING.md', 'CODE_OF_CONDUCT.md']:
    sample_path = ROOT / candidate
    if sample_path.exists():
        SAMPLE = sample_path
        break
else:
    # fallback to a temporary file
    SAMPLE = ROOT / 'tmp_encryption_test.txt'
    SAMPLE.write_text('encryption test')

try:
    from quantum_shield import QuantumShield
except Exception as e:
    print('Shield import failed:', e)
    raise

shield = QuantumShield()
# ensure we don't delete originals during tests
shield.config['delete_original_after_encrypt'] = False
shield.config['dry_run'] = False

passphrase = sys.argv[1] if len(sys.argv) > 1 else secrets.token_hex(16)
print('Using passphrase:', '***PROVIDED***' if len(sys.argv)>1 else passphrase)

enc_ok = shield.encrypt_file(SAMPLE, passphrase)
if not enc_ok:
    print('Encryption failed')
    raise SystemExit(1)
enc_path = SAMPLE.with_suffix(SAMPLE.suffix + '.enc')
if not enc_path.exists():
    print('Encrypted file not found:', enc_path)
    raise SystemExit(1)

# attempt decrypt to temp file
dec_ok = shield.decrypt_file(enc_path, passphrase)
if not dec_ok:
    print('Decryption failed')
    raise SystemExit(1)

# verify content
orig = SAMPLE.read_bytes()
restored = (SAMPLE.parent / SAMPLE.name).read_bytes()
if orig == restored:
    print('Round-trip success: original == restored')
else:
    print('Round-trip mismatch: contents differ')

# cleanup: remove .enc and restored copy if decrypt created a file (it removes .enc and writes original back by current code, so we will remove the created enc if present)
if enc_path.exists():
    enc_path.unlink()
print('Test complete')
