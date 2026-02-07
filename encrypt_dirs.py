#!/usr/bin/env python3
from pathlib import Path
import sys

from quantum_shield import QuantumShield


def main(argv):
    if len(argv) < 2:
        print('Usage: encrypt_dirs.py <passphrase> [--delete]')
        return 1

    passphrase = argv[1]
    delete = '--delete' in argv

    shield = QuantumShield()
    shield.config['dry_run'] = False
    shield.config['delete_original_after_encrypt'] = delete

    dirs = [
        'enterprise/departments/executive',
        'enterprise/departments/legal-compliance'
    ]

    total_encrypted = 0
    total_skipped = 0

    for d in dirs:
        p = Path(d)
        if not p.exists():
            print(f'⚠️  Directory not found: {p}')
            continue
        print(f'🔒 Scanning and encrypting: {p}')
        enc, skip = shield.scan_and_encrypt_directory(p, passphrase)
        print(f'  ✅ Encrypted: {enc}  ⏭ Skipped: {skip}')
        total_encrypted += enc
        total_skipped += skip

    print('\nSummary:')
    print(f'  Total encrypted: {total_encrypted}')
    print(f'  Total skipped : {total_skipped}')

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))