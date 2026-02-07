#!/usr/bin/env python3
"""
Shield Test Suite - Automatic validation on every run
Original implementation for accuracy verification
"""

import hashlib
import json
from pathlib import Path
from datetime import datetime

class ShieldTestValidator:
    """Validates encryption accuracy with dense data and complex math"""
    
    def __init__(self):
        self.test_data_dir = Path(__file__).parent / 'test_data'
        self.test_results_file = Path.home() / '.artifact_shield' / 'test_results.json'
        
    def generate_dense_test_content(self):
        """Generate test content with dense data and complex mathematics"""
        content_parts = []
        
        # Dense textual data
        content_parts.append("=" * 80)
        content_parts.append("SHIELD VALIDATION TEST FILE")
        content_parts.append("Classification: TOP_SECRET")
        content_parts.append("=" * 80)
        content_parts.append("")
        
        # Complex mathematical expressions
        content_parts.append("## Mathematical Validation Data")
        content_parts.append("")
        content_parts.append("Prime numbers sequence:")
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
        content_parts.append(" ".join(str(p) for p in primes))
        content_parts.append("")
        
        # Fibonacci sequence
        content_parts.append("Fibonacci sequence:")
        fib_nums = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610]
        content_parts.append(" ".join(str(f) for f in fib_nums))
        content_parts.append("")
        
        # Complex calculations
        content_parts.append("Complex calculations:")
        for i in range(1, 11):
            result = (i ** 3) + (i ** 2) - (i * 7) + 42
            content_parts.append(f"f({i}) = {i}^3 + {i}^2 - {i}*7 + 42 = {result}")
        content_parts.append("")
        
        # Dense data patterns
        content_parts.append("## Dense Data Patterns")
        content_parts.append("")
        
        # Binary patterns
        content_parts.append("Binary sequence:")
        for i in range(16):
            binary = bin(i)[2:].zfill(8)
            content_parts.append(f"{i:2d}: {binary}")
        content_parts.append("")
        
        # Hexadecimal checksums
        content_parts.append("Hexadecimal test vectors:")
        test_strings = ["Shield", "Quantum", "Encryption", "Security", "Artifact"]
        for s in test_strings:
            hex_val = hashlib.sha256(s.encode()).hexdigest()[:16]
            content_parts.append(f"{s:12s} -> {hex_val}")
        content_parts.append("")
        
        # Unicode and special characters
        content_parts.append("## Unicode and Special Characters")
        content_parts.append("")
        content_parts.append("Mathematical symbols: ∑ ∫ ∂ ∇ √ ∞ ≈ ≠ ≤ ≥")
        content_parts.append("Greek letters: α β γ δ ε ζ η θ ι κ λ μ ν ξ ο π ρ σ τ υ φ χ ψ ω")
        content_parts.append("Currency: $ € £ ¥ ₹ ₽ ₿")
        content_parts.append("Arrows: → ← ↑ ↓ ↔ ⇒ ⇐ ⇔")
        content_parts.append("")
        
        # JSON structure
        content_parts.append("## Structured Data")
        content_parts.append("")
        test_json = {
            "shield_version": "1.0.0",
            "test_timestamp": datetime.now().isoformat(),
            "numeric_data": [1.414, 2.718, 3.142, 6.626e-34],
            "nested": {
                "level1": {
                    "level2": {
                        "value": "deeply_nested_data"
                    }
                }
            }
        }
        content_parts.append(json.dumps(test_json, indent=2))
        content_parts.append("")
        
        # Large text block
        content_parts.append("## Dense Text Block")
        content_parts.append("")
        lorem_base = "Lorem ipsum dolor sit amet consectetur adipiscing elit"
        content_parts.append(" ".join([lorem_base] * 20))
        content_parts.append("")
        
        # Verification checksum
        full_content = "\n".join(content_parts)
        checksum = hashlib.sha256(full_content.encode()).hexdigest()
        content_parts.append("")
        content_parts.append(f"## Verification Checksum")
        content_parts.append(f"SHA256: {checksum}")
        
        return "\n".join(content_parts)
    
    def run_validation_cycle(self, shield_instance):
        """Run complete encrypt-decrypt validation cycle"""
        validation_results = {
            "timestamp": datetime.now().isoformat(),
            "tests": []
        }
        
        print("🧪 Running Shield Validation Tests...")
        print("")
        
        # Test 1: Dense data encryption accuracy
        test_result_1 = self.test_dense_data_encryption(shield_instance)
        validation_results["tests"].append(test_result_1)
        
        # Test 2: Mathematical accuracy preservation
        test_result_2 = self.test_mathematical_accuracy(shield_instance)
        validation_results["tests"].append(test_result_2)
        
        # Test 3: Special characters handling
        test_result_3 = self.test_special_characters(shield_instance)
        validation_results["tests"].append(test_result_3)
        
        # Test 4: Large file handling
        test_result_4 = self.test_large_file(shield_instance)
        validation_results["tests"].append(test_result_4)
        
        # Calculate overall success
        passed_tests = sum(1 for t in validation_results["tests"] if t["passed"])
        total_tests = len(validation_results["tests"])
        validation_results["success_rate"] = (passed_tests / total_tests) * 100
        
        # Save results
        self.save_test_results(validation_results)
        
        # Display summary
        self.display_test_summary(validation_results)
        
        return validation_results["success_rate"] == 100.0
    
    def test_dense_data_encryption(self, shield_instance):
        """Test encryption/decryption with dense data"""
        test_name = "Dense Data Encryption Accuracy"
        
        try:
            # Generate test content
            original_content = self.generate_dense_test_content()
            original_bytes = original_content.encode('utf-8')
            
            # Test passphrase
            test_passphrase = "TestPass123!@#"
            
            # Encrypt
            encrypted_data = shield_instance.encrypt_data(original_bytes, test_passphrase)
            
            # Decrypt
            decrypted_data = shield_instance.decrypt_data(encrypted_data, test_passphrase)
            
            # Verify
            if decrypted_data == original_bytes:
                print(f"✅ {test_name}: PASSED")
                return {
                    "name": test_name,
                    "passed": True,
                    "message": "Dense data encrypted and decrypted successfully",
                    "bytes_processed": len(original_bytes)
                }
            else:
                print(f"❌ {test_name}: FAILED - Data mismatch")
                return {
                    "name": test_name,
                    "passed": False,
                    "message": "Decrypted data does not match original",
                    "bytes_processed": len(original_bytes)
                }
        
        except Exception as error:
            print(f"❌ {test_name}: FAILED - {error}")
            return {
                "name": test_name,
                "passed": False,
                "message": str(error),
                "bytes_processed": 0
            }
    
    def test_mathematical_accuracy(self, shield_instance):
        """Test that mathematical calculations are preserved"""
        test_name = "Mathematical Accuracy Preservation"
        
        try:
            # Create content with precise calculations
            calc_lines = []
            for i in range(1, 51):
                result = (i ** 3) - (i ** 2) + (i * 13) - 7
                calc_lines.append(f"{i},{result}")
            
            original_content = "\n".join(calc_lines)
            original_bytes = original_content.encode('utf-8')
            
            # Encrypt and decrypt
            test_passphrase = "MathTest789"
            encrypted_data = shield_instance.encrypt_data(original_bytes, test_passphrase)
            decrypted_data = shield_instance.decrypt_data(encrypted_data, test_passphrase)
            
            # Verify each calculation
            if decrypted_data == original_bytes:
                decrypted_content = decrypted_data.decode('utf-8')
                lines = decrypted_content.split('\n')
                
                all_correct = True
                for line in lines:
                    parts = line.split(',')
                    if len(parts) == 2:
                        i = int(parts[0])
                        expected = (i ** 3) - (i ** 2) + (i * 13) - 7
                        actual = int(parts[1])
                        if expected != actual:
                            all_correct = False
                            break
                
                if all_correct:
                    print(f"✅ {test_name}: PASSED")
                    return {
                        "name": test_name,
                        "passed": True,
                        "message": "All mathematical calculations preserved accurately",
                        "calculations_verified": len(lines)
                    }
                else:
                    print(f"❌ {test_name}: FAILED - Calculation error")
                    return {
                        "name": test_name,
                        "passed": False,
                        "message": "Mathematical calculation mismatch detected"
                    }
            else:
                print(f"❌ {test_name}: FAILED - Data corruption")
                return {
                    "name": test_name,
                    "passed": False,
                    "message": "Data corruption detected"
                }
        
        except Exception as error:
            print(f"❌ {test_name}: FAILED - {error}")
            return {
                "name": test_name,
                "passed": False,
                "message": str(error)
            }
    
    def test_special_characters(self, shield_instance):
        """Test handling of special characters and Unicode"""
        test_name = "Special Characters & Unicode"
        
        try:
            # Test content with various special characters
            test_content = (
                "Mathematical: ∑∫∂∇√∞≈≠≤≥\n"
                "Greek: αβγδεζηθικλμνξοπρστυφχψω\n"
                "Currency: $€£¥₹₽₿\n"
                "Arrows: →←↑↓↔⇒⇐⇔\n"
                "Symbols: ™©®℠℗§¶†‡\n"
                "Emoji: 🛡️🔒🔐🗝️💻🚀\n"
            )
            
            original_bytes = test_content.encode('utf-8')
            test_passphrase = "Unicode@Test#456"
            
            # Encrypt and decrypt
            encrypted_data = shield_instance.encrypt_data(original_bytes, test_passphrase)
            decrypted_data = shield_instance.decrypt_data(encrypted_data, test_passphrase)
            
            if decrypted_data == original_bytes:
                print(f"✅ {test_name}: PASSED")
                return {
                    "name": test_name,
                    "passed": True,
                    "message": "All special characters preserved correctly"
                }
            else:
                print(f"❌ {test_name}: FAILED")
                return {
                    "name": test_name,
                    "passed": False,
                    "message": "Special character corruption detected"
                }
        
        except Exception as error:
            print(f"❌ {test_name}: FAILED - {error}")
            return {
                "name": test_name,
                "passed": False,
                "message": str(error)
            }
    
    def test_large_file(self, shield_instance):
        """Test handling of large files"""
        test_name = "Large File Handling"
        
        try:
            # Generate large content (1MB)
            chunk = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789" * 100
            large_content = (chunk + "\n") * 300  # ~1MB
            
            original_bytes = large_content.encode('utf-8')
            test_passphrase = "LargeFile!Pass"
            
            # Encrypt and decrypt
            encrypted_data = shield_instance.encrypt_data(original_bytes, test_passphrase)
            decrypted_data = shield_instance.decrypt_data(encrypted_data, test_passphrase)
            
            # Verify with checksum
            original_checksum = hashlib.sha256(original_bytes).hexdigest()
            decrypted_checksum = hashlib.sha256(decrypted_data).hexdigest()
            
            if original_checksum == decrypted_checksum:
                print(f"✅ {test_name}: PASSED ({len(original_bytes):,} bytes)")
                return {
                    "name": test_name,
                    "passed": True,
                    "message": f"Large file ({len(original_bytes):,} bytes) handled correctly",
                    "file_size": len(original_bytes)
                }
            else:
                print(f"❌ {test_name}: FAILED")
                return {
                    "name": test_name,
                    "passed": False,
                    "message": "Large file corruption detected"
                }
        
        except Exception as error:
            print(f"❌ {test_name}: FAILED - {error}")
            return {
                "name": test_name,
                "passed": False,
                "message": str(error)
            }
    
    def save_test_results(self, results):
        """Save test results to file"""
        try:
            self.test_results_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.test_results_file, 'w') as f:
                json.dump(results, f, indent=2)
        except Exception:
            pass  # Fail silently
    
    def display_test_summary(self, results):
        """Display test summary"""
        print("")
        print("=" * 60)
        print("SHIELD VALIDATION SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for t in results["tests"] if t["passed"])
        total = len(results["tests"])
        
        print(f"Tests Run: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {results['success_rate']:.1f}%")
        print("")
        
        if results["success_rate"] == 100.0:
            print("✅ All validation tests passed - Shield is operating correctly")
        else:
            print("⚠️  Some tests failed - Review test results")
        
        print("=" * 60)
        print("")
