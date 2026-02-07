#!/usr/bin/env python3
"""Encrypt a given file with QuantumShield and validate round-trip decryption.
Usage: python scripts/shield/encrypt_and_validate_file.py <file> <passphrase>
"""
import sys
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
try:
    from quantum_shield import QuantumShield
except Exception as e:
    print('Shield import failed:', e)
    raise

if len(sys.argv) < 3:
    print('Usage: encrypt_and_validate_file.py <file> <passphrase>')
    raise SystemExit(1)

file_path = Path(sys.argv[1])
passphrase = sys.argv[2]

if not file_path.exists():
    print('File not found:', file_path)
    raise SystemExit(1)

shield = QuantumShield()
# safe settings
shield.config['delete_original_after_encrypt'] = False
shield.config['dry_run'] = False

# copy original to temp for verification
tmp_orig = file_path.with_suffix(file_path.suffix + '.orig.tmp')
shutil.copy2(file_path, tmp_orig)

print(f'Encrypting {file_path}...')
if not shield.encrypt_file(file_path, passphrase):
    print('Encryption failed')
    tmp_orig.unlink(missing_ok=True)
    raise SystemExit(1)

enc_path = file_path.with_suffix(file_path.suffix + '.enc')
if not enc_path.exists():
    print('Encrypted file missing:', enc_path)
    tmp_orig.unlink(missing_ok=True)
    raise SystemExit(1)

print('Decrypting to verify...')
# decrypt will write original file back and remove .enc
if not shield.decrypt_file(enc_path, passphrase):
    print('Decryption failed')
    tmp_orig.unlink(missing_ok=True)
    raise SystemExit(1)

# now compare
if file_path.exists():
    orig_bytes = tmp_orig.read_bytes()
    new_bytes = file_path.read_bytes()
    if orig_bytes == new_bytes:
        print('Round-trip success: contents match')
    else:
        print('Round-trip mismatch: contents differ')
        tmp_orig.unlink(missing_ok=True)
        raise SystemExit(1)
else:
    print('Decrypted file not found after decrypt process')
    tmp_orig.unlink(missing_ok=True)
    raise SystemExit(1)

# cleanup temp
tmp_orig.unlink(missing_ok=True)
print('Validation complete')
