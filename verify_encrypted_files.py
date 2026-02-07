#!/usr/bin/env python3
"""Verify that encrypted (.enc) files decrypt correctly and match originals from a backup zip.
Usage: python scripts/shield/verify_encrypted_files.py <backup-zip-path> <passphrase>
"""
import sys
import json
import shutil
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / 'csv-manifest.json'

if len(sys.argv) < 3:
    print('Usage: verify_encrypted_files.py <backup-zip-path> <passphrase>')
    raise SystemExit(1)

backup = Path(sys.argv[1])
passphrase = sys.argv[2]

if not backup.exists():
    print('Backup not found:', backup)
    raise SystemExit(1)

try:
    from quantum_shield import QuantumShield
except Exception as e:
    print('Shield import failed:', e)
    raise

s = QuantumShield()

with ZipFile(backup, 'r') as zf:
    tmpdir = ROOT / 'tmp_verify'
    if tmpdir.exists():
        shutil.rmtree(tmpdir)
    tmpdir.mkdir()
    zf.extractall(path=tmpdir)

    manifest = json.load(open(MANIFEST))
    failed = False
    for it in manifest:
        if not it.get('sensitive'):
            continue
        rel = Path(it['path'])
        enc_path = ROOT / (str(rel) + '.enc')
        if not enc_path.exists():
            print('Missing .enc for', rel)
            failed = True
            continue
        # copy enc to temp and decrypt
        test_enc = tmpdir / (enc_path.name)
        shutil.copy2(enc_path, test_enc)
        ok = s.decrypt_file(test_enc, passphrase)
        if not ok:
            print('Decryption failed for', enc_path)
            failed = True
            continue
        # compare restored file (in tmpdir path)
        restored = test_enc.with_suffix('')  # decrypted wrote this
        orig_from_backup = tmpdir / rel
        if not orig_from_backup.exists():
            print('Original not present in backup for', rel)
            failed = True
            continue
        if restored.exists():
            if restored.read_bytes() == orig_from_backup.read_bytes():
                print('Verified:', rel)
            else:
                print('Mismatch after decrypt for', rel)
                failed = True
            restored.unlink()
        else:
            print('Restored file missing:', restored)
            failed = True

    shutil.rmtree(tmpdir, ignore_errors=True)

if failed:
    print('Verification completed: FAIL')
    raise SystemExit(1)
else:
    print('Verification completed: SUCCESS')
    sys.exit(0)
