#!/usr/bin/env python3
from pathlib import Path
from quantum_shield import QuantumShield

s = QuantumShield()
import os, sys
passphrase = os.environ.get('SHIELD_PASSPHRASE') or (sys.argv[1] if len(sys.argv) > 1 else None)
if not passphrase:
    print("Usage: verify_sample_decrypt.py <passphrase> or set SHIELD_PASSPHRASE in env")
    sys.exit(1)
paths = list(Path('enterprise/departments/executive').rglob('*.enc')) + list(Path('enterprise/departments/legal-compliance').rglob('*.enc'))
print('Found .enc files:', len(paths))
ok = 0
for i,p in enumerate(sorted(paths)[:100]):
    b = p.read_bytes()
    dec = s.decrypt_data(b, passphrase)
    status = 'OK' if dec else 'FAIL'
    print(f'{i+1}. {p} -> {status}')
    if dec:
        ok += 1
print(f'OK: {ok} / {len(paths)} (checked up to 100)')
