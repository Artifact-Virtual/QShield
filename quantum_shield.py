#!/usr/bin/env python3
"""
Artifact Virtual Quantum Shield - Encryption/Decryption System
Original implementation - No public code references
"""

import os
import sys
import json
import hashlib
import secrets
from pathlib import Path
from datetime import datetime

# Configuration paths
SHIELD_DIR = Path.home() / '.artifact_shield'
CONFIG_FILE = SHIELD_DIR / 'config.json'
KEY_FILE = SHIELD_DIR / 'keystore.dat'
AUDIT_LOG = SHIELD_DIR / 'audit.log'

class QuantumShield:
    """Multi-layer encryption system with self-healing capabilities"""
    
    def __init__(self):
        self.ensure_shield_directory()
        self.config = self.load_or_create_config()
        
    def ensure_shield_directory(self):
        """Self-healing: Create shield directory if missing"""
        SHIELD_DIR.mkdir(parents=True, exist_ok=True)
        
        # Create .gitignore to protect keys
        gitignore_path = SHIELD_DIR / '.gitignore'
        if not gitignore_path.exists():
            gitignore_path.write_text('*\n!.gitignore\n')
    
    def load_or_create_config(self):
        """Load config or create default - fail-proof"""
        try:
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
        except Exception as error:
            self.log_event(f'Config load failed: {error}')
        
        # Default configuration
        default_config = {
            'version': '1.0.0',
            'min_key_length': 12,                # raise minimal passphrase length for safety
            'max_key_length': 1000,
            'auto_encrypt': False,               # opt-out safe default
            'delete_original_after_encrypt': False, # do not delete originals by default
            'classifications': ['TOP_SECRET', 'CONFIDENTIAL', 'RESTRICTED'],
            'exclude_patterns': ['.shield', 'backups', 'scripts/shield', 'node_modules', '.git'],
            'encryption_marker': 'ARTIFACT_SHIELD_ENCRYPTED',
            'dry_run': False                      # CI and tests should use dry-run by default
        }
        
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(default_config, f, indent=2)
        except Exception as error:
            self.log_event(f'Config save failed: {error}')
        
        return default_config
    
    def log_event(self, message):
        """Fail-proof audit logging"""
        try:
            timestamp = datetime.now().isoformat()
            log_entry = f'{timestamp} | {message}\n'
            with open(AUDIT_LOG, 'a') as f:
                f.write(log_entry)
        except Exception:
            # Never fail on logging
            pass
    
    def derive_encryption_key(self, user_passphrase, file_salt):
        """Original key derivation - multi-round hashing"""
        combined = f'{user_passphrase}::{file_salt}'.encode('utf-8')
        
        # Multiple rounds of different hash algorithms for strength
        round1 = hashlib.sha3_512(combined).digest()
        round2 = hashlib.blake2b(round1, digest_size=64).digest()
        round3 = hashlib.sha512(round2).digest()
        
        return round3
    
    def encrypt_data(self, plaintext_bytes, user_key):
        """Original encryption using multi-layer XOR with derived keys"""
        file_salt = secrets.token_hex(32)
        encryption_key = self.derive_encryption_key(user_key, file_salt)
        
        # Multi-layer encryption
        encrypted = bytearray(plaintext_bytes)
        key_length = len(encryption_key)
        
        # Layer 1: XOR with derived key
        for i in range(len(encrypted)):
            encrypted[i] ^= encryption_key[i % key_length]
        
        # Layer 2: Reverse XOR for additional complexity
        for i in range(len(encrypted) - 1, -1, -1):
            encrypted[i] ^= encryption_key[(len(encrypted) - i - 1) % key_length]
        
        # Layer 3: Position-dependent XOR
        for i in range(len(encrypted)):
            position_factor = (i + 1) % 256
            encrypted[i] ^= position_factor
        
        # Package with metadata
        marker = self.config['encryption_marker'].encode('utf-8')
        version = b'v1.0'
        salt_bytes = file_salt.encode('utf-8')
        
        package = marker + b'::' + version + b'::' + salt_bytes + b'::' + bytes(encrypted)
        return package
    
    def decrypt_data(self, encrypted_package, user_key):
        """Original decryption - reverse of encryption process"""
        try:
            # Parse package
            parts = encrypted_package.split(b'::', 3)
            if len(parts) != 4:
                return None
            
            marker, version, salt_bytes, encrypted = parts
            
            # Verify marker
            if marker.decode('utf-8') != self.config['encryption_marker']:
                return None
            
            file_salt = salt_bytes.decode('utf-8')
            encryption_key = self.derive_encryption_key(user_key, file_salt)
            
            # Reverse layer 3: Position-dependent XOR
            decrypted = bytearray(encrypted)
            for i in range(len(decrypted)):
                position_factor = (i + 1) % 256
                decrypted[i] ^= position_factor
            
            # Reverse layer 2: Reverse XOR
            key_length = len(encryption_key)
            for i in range(len(decrypted) - 1, -1, -1):
                decrypted[i] ^= encryption_key[(len(decrypted) - i - 1) % key_length]
            
            # Reverse layer 1: XOR with derived key
            for i in range(len(decrypted)):
                decrypted[i] ^= encryption_key[i % key_length]
            
            return bytes(decrypted)
        except Exception as error:
            self.log_event(f'Decryption failed: {error}')
            return None
    
    def is_encrypted(self, file_path):
        """Check if file is already encrypted"""
        try:
            with open(file_path, 'rb') as f:
                header = f.read(100)
                return self.config['encryption_marker'].encode('utf-8') in header
        except Exception:
            return False
    
    def should_exclude(self, file_path):
        """Check if file should be excluded from encryption"""
        file_str = str(file_path)
        for pattern in self.config['exclude_patterns']:
            if pattern in file_str:
                return True
        
        # Don't encrypt the encryption tool itself
        if file_str.endswith('quantum_shield.py'):
            return True
        
        return False
    
    def get_passphrase(self, prompt='Enter passphrase: '):
        """Get passphrase from user with validation"""
        import getpass
        
        while True:
            passphrase = getpass.getpass(prompt)
            
            if len(passphrase) < self.config['min_key_length']:
                print(f'⚠️  Passphrase too short (minimum {self.config["min_key_length"]} characters)')
                continue
            
            if len(passphrase) > self.config['max_key_length']:
                print(f'⚠️  Passphrase too long (maximum {self.config["max_key_length"]} characters)')
                continue
            
            return passphrase
    
    def encrypt_file(self, file_path, user_key):
        """Encrypt a single file - fail-proof"""
        try:
            file_path = Path(file_path)
            
            # Check exclusions
            if self.should_exclude(file_path):
                self.log_event(f'Skipped (excluded): {file_path}')
                return False
            
            # Check if already encrypted
            if self.is_encrypted(file_path):
                self.log_event(f'Already encrypted: {file_path}')
                return True
            
            # Read plaintext
            with open(file_path, 'rb') as f:
                plaintext = f.read()
            
            # Encrypt
            encrypted = self.encrypt_data(plaintext, user_key)
            
            # Write encrypted
            encrypted_path = file_path.parent / (file_path.name + '.enc')
            with open(encrypted_path, 'wb') as f:
                f.write(encrypted)
            
            # Optionally remove original only if configured
            if self.config.get('delete_original_after_encrypt') and not self.config.get('dry_run'):
                try:
                    file_path.unlink()
                except Exception as e:
                    self.log_event(f'Failed to remove original {file_path}: {e}')
            
            self.log_event(f'Encrypted: {file_path} -> {encrypted_path}')
            return True
            
        except Exception as error:
            self.log_event(f'Encryption error for {file_path}: {error}')
            return False
    
    def decrypt_file(self, file_path, user_key):
        """Decrypt a single file - fail-proof"""
        try:
            file_path = Path(file_path)
            
            # Ensure it's an encrypted file
            if not str(file_path).endswith('.enc'):
                print(f'⚠️  Not an encrypted file: {file_path}')
                return False
            
            # Read encrypted
            with open(file_path, 'rb') as f:
                encrypted = f.read()
            
            # Decrypt
            plaintext = self.decrypt_data(encrypted, user_key)
            
            if plaintext is None:
                print(f'❌ Decryption failed: {file_path} (wrong passphrase?)')
                return False
            
            # Write plaintext
            original_path = file_path.parent / file_path.stem  # Remove .enc
            with open(original_path, 'wb') as f:
                f.write(plaintext)
            
            # Remove encrypted
            file_path.unlink()
            
            self.log_event(f'Decrypted: {file_path} -> {original_path}')
            return True
            
        except Exception as error:
            self.log_event(f'Decryption error for {file_path}: {error}')
            return False
    
    def scan_and_encrypt_directory(self, directory, user_key, classification=None):
        """Scan directory and encrypt classified files"""
        directory = Path(directory)
        encrypted_count = 0
        skipped_count = 0
        
        for file_path in directory.rglob('*'):
            if not file_path.is_file():
                continue
            
            # Check if file should be encrypted based on classification
            if classification:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        first_lines = f.read(500)
                        if classification not in first_lines:
                            continue
                except Exception:
                    continue
            
            if self.encrypt_file(file_path, user_key):
                encrypted_count += 1
            else:
                skipped_count += 1
        
        return encrypted_count, skipped_count
    
    def display_banner(self):
        """Display shield banner"""
        banner = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║     🛡️  ARTIFACT VIRTUAL QUANTUM SHIELD 🛡️                   ║
║                                                               ║
║           Multi-Layer Encryption System v1.0                  ║
║              Protecting Your Secrets                          ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
"""
        print(banner)
    
    def display_menu(self):
        """Display interactive menu"""
        menu = """
┌───────────────────────────────────────────────────────────────┐
│                      MAIN MENU                                │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│  [1] Encrypt File                                             │
│  [2] Decrypt File                                             │
│  [3] Encrypt Directory                                        │
│  [4] Encrypt by Classification (TOP_SECRET, CONFIDENTIAL)     │
│  [5] Check Encryption Status                                  │
│  [6] View Audit Log                                           │
│  [7] Configuration                                            │
│  [0] Exit                                                     │
│                                                               │
└───────────────────────────────────────────────────────────────┘
"""
        print(menu)
    
    def run_interactive(self):
        """Run interactive terminal UI"""
        self.display_banner()
        
        while True:
            self.display_menu()
            choice = input('\n🔐 Select option: ').strip()
            
            if choice == '0':
                print('\n✅ Shield deactivated. Stay secure!')
                break
            
            elif choice == '1':
                file_path = input('📄 Enter file path: ').strip()
                if not Path(file_path).exists():
                    print('❌ File not found')
                    continue
                
                if self.is_encrypted(file_path):
                    print('ℹ️  File is already encrypted')
                    continue
                
                passphrase = self.get_passphrase('🔑 Enter passphrase for encryption: ')
                
                if self.encrypt_file(file_path, passphrase):
                    print(f'✅ Encrypted: {file_path}')
                else:
                    print(f'❌ Encryption failed')
            
            elif choice == '2':
                file_path = input('📄 Enter encrypted file path (.enc): ').strip()
                if not Path(file_path).exists():
                    print('❌ File not found')
                    continue
                
                passphrase = self.get_passphrase('🔑 Enter passphrase for decryption: ')
                
                if self.decrypt_file(file_path, passphrase):
                    print(f'✅ Decrypted: {file_path}')
                else:
                    print(f'❌ Decryption failed')
            
            elif choice == '3':
                directory = input('📁 Enter directory path: ').strip()
                if not Path(directory).exists():
                    print('❌ Directory not found')
                    continue
                
                passphrase = self.get_passphrase('🔑 Enter passphrase: ')
                
                print(f'\n🔄 Scanning and encrypting...')
                encrypted, skipped = self.scan_and_encrypt_directory(directory, passphrase)
                print(f'✅ Encrypted: {encrypted} files')
                print(f'ℹ️  Skipped: {skipped} files')
            
            elif choice == '4':
                print('\nAvailable classifications:')
                for i, classification in enumerate(self.config['classifications'], 1):
                    print(f'  [{i}] {classification}')
                
                class_choice = input('Select classification number: ').strip()
                try:
                    class_index = int(class_choice) - 1
                    classification = self.config['classifications'][class_index]
                except (ValueError, IndexError):
                    print('❌ Invalid selection')
                    continue
                
                directory = input('📁 Enter directory to scan: ').strip() or '.'
                passphrase = self.get_passphrase('🔑 Enter passphrase: ')
                
                print(f'\n🔄 Scanning for {classification} files...')
                encrypted, skipped = self.scan_and_encrypt_directory(
                    directory, passphrase, classification
                )
                print(f'✅ Encrypted: {encrypted} {classification} files')
            
            elif choice == '5':
                directory = input('📁 Enter directory to check (default: .): ').strip() or '.'
                directory = Path(directory)
                
                encrypted_files = []
                plaintext_files = []
                
                for file_path in directory.rglob('*'):
                    if not file_path.is_file():
                        continue
                    
                    if self.should_exclude(file_path):
                        continue
                    
                    if str(file_path).endswith('.enc') or self.is_encrypted(file_path):
                        encrypted_files.append(file_path)
                    else:
                        plaintext_files.append(file_path)
                
                print(f'\n📊 Encryption Status for {directory}:')
                print(f'  🔒 Encrypted: {len(encrypted_files)} files')
                print(f'  📄 Plaintext: {len(plaintext_files)} files')
                
                if plaintext_files and len(plaintext_files) <= 10:
                    print('\n⚠️  Unencrypted files:')
                    for f in plaintext_files:
                        print(f'    - {f}')
            
            elif choice == '6':
                if AUDIT_LOG.exists():
                    print('\n📋 Recent Audit Log Entries:\n')
                    with open(AUDIT_LOG, 'r') as f:
                        lines = f.readlines()
                        for line in lines[-20:]:  # Last 20 entries
                            print(f'  {line.strip()}')
                else:
                    print('ℹ️  No audit log found')
            
            elif choice == '7':
                print('\n⚙️  Current Configuration:')
                print(json.dumps(self.config, indent=2))
                print(f'\n📁 Config file: {CONFIG_FILE}')
                print(f'📁 Audit log: {AUDIT_LOG}')
            
            else:
                print('❌ Invalid option')
            
            input('\nPress Enter to continue...')
            print('\n' * 2)


def main():
    """Main entry point"""
    shield = QuantumShield()
    
    # Run automatic validation tests (dry mode - always runs)
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from test_validator import ShieldTestValidator
        
        validator = ShieldTestValidator()
        validation_passed = validator.run_validation_cycle(shield)
        
        if not validation_passed:
            print("\n⚠️  Warning: Some validation tests failed")
            print("   Shield is still operational but accuracy may be compromised")
            proceed = input("\n   Continue anyway? (y/N): ").strip().lower()
            if proceed != 'y':
                print("   Exiting...")
                return 1
        print("")
    except ImportError:
        # Validator not available, continue without validation
        pass
    except Exception as validation_error:
        print(f"\n⚠️  Validation error: {validation_error}")
        print("   Continuing with shield operation...\n")
    
    # Check command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'encrypt' and len(sys.argv) > 2:
            file_path = sys.argv[2]
            passphrase = shield.get_passphrase()
            shield.encrypt_file(file_path, passphrase)
        
        elif command == 'decrypt' and len(sys.argv) > 2:
            file_path = sys.argv[2]
            passphrase = shield.get_passphrase()
            shield.decrypt_file(file_path, passphrase)
        
        elif command == 'status':
            directory = sys.argv[2] if len(sys.argv) > 2 else '.'
            # Status check logic here
            print(f'Checking status of {directory}...')
        
        else:
            print('Usage: quantum_shield.py [encrypt|decrypt|status] <file>')
    else:
        # Run interactive mode
        shield.run_interactive()


if __name__ == '__main__':
    main()
