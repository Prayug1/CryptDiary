import os
import time
import tempfile
import shutil
import statistics
from contextlib import contextmanager

# Import CryptDiary modules
from user_manager import UserManager
from key_manager import KeyManager
from crypto_manager import CryptoManager
from diary_storage import DiaryStorage


# ----------------------------------------------------------------------
# Utility timing functions
# ----------------------------------------------------------------------
@contextmanager
def timer(label, results_dict):
    """Simple context manager to time a block of code once."""
    start = time.perf_counter()
    yield
    elapsed = time.perf_counter() - start
    results_dict[label] = elapsed
    print(f"{label:40s} : {elapsed*1000:8.3f} ms")


def timed_func(func, *args, repeats=5, **kwargs):
    """
    Run a function multiple times and return (average_time, last_result).
    The function is called with *args and **kwargs for each repetition.
    """
    times = []
    result = None
    for _ in range(repeats):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        times.append(time.perf_counter() - start)
    avg_time = statistics.mean(times)
    return avg_time, result


# ----------------------------------------------------------------------
# Test data generation
# ----------------------------------------------------------------------
def generate_test_data(size_kb):
    """Generate a string of given size in KB."""
    return "x" * (size_kb * 1024)


# ----------------------------------------------------------------------
# Main performance test
# ----------------------------------------------------------------------
def run_performance_tests():
    results = {}

    # Create a temporary directory for all test files
    temp_dir = tempfile.mkdtemp(prefix="cryptdiary_perf_")
    print(f"Using temporary directory: {temp_dir}")

    try:
        # ------------------------------------------------------------------
        # 1. User registration (includes key generation, certificate, keystore)
        #    Only one registration needed.
        # ------------------------------------------------------------------
        user_manager = UserManager(users_dir=os.path.join(temp_dir, "users"))
        with timer("User Registration (RSA 2048 + cert + keystore)", results):
            user_manager.register_user("perf_test_user", "testpass123", "Perf User")

        # ------------------------------------------------------------------
        # 2. Key loading (keystore decryption)
        #    Average over 3 loads.
        # ------------------------------------------------------------------
        key_manager = KeyManager(user_dir=user_manager.get_user_dir("perf_test_user"))
        load_time, _ = timed_func(key_manager.load_keystore, "testpass123", repeats=3)
        results["Load keystore (decrypt + load keys)"] = load_time
        print(f"{'Load keystore (decrypt + load keys)':40s} : {load_time*1000:8.3f} ms")

        # Ensure keys are loaded for subsequent tests
        if not key_manager.private_key:
            raise RuntimeError("Failed to load keys")

        crypto_manager = CryptoManager(key_manager)

        # ------------------------------------------------------------------
        # 3. RSA operations (sign/verify) with small data (average over 10 runs)
        # ------------------------------------------------------------------
        test_data = b"Hello, this is a test message for signing."
        # Signing
        sign_time, signature_info = timed_func(crypto_manager.sign_entry, test_data, repeats=10)
        results["Sign data (RSA PSS SHA256)"] = sign_time
        print(f"{'Sign data (RSA PSS SHA256)':40s} : {sign_time*1000:8.3f} ms")

        # Verification (using own public key)
        verify_time, _ = timed_func(
            crypto_manager.verify_signature,
            test_data,
            signature_info['signature'],
            signature_info['signed_timestamp'],
            cert_serial=signature_info['cert_serial'],
            repeats=10
        )
        results["Verify signature (RSA PSS SHA256)"] = verify_time
        print(f"{'Verify signature (RSA PSS SHA256)':40s} : {verify_time*1000:8.3f} ms")

        # ------------------------------------------------------------------
        # 4. Encryption / Decryption with various data sizes (average over 5 runs each)
        # ------------------------------------------------------------------
        sizes_kb = [1, 10, 100, 500]   # 1KB, 10KB, 100KB, 500KB
        for size in sizes_kb:
            plain = generate_test_data(size)

            # Encryption
            enc_time, encrypted = timed_func(crypto_manager.encrypt_entry, plain, repeats=5)
            results[f"Encrypt {size:4} KB (hybrid RSA+AES)"] = enc_time
            print(f"{f'Encrypt {size:4} KB (hybrid RSA+AES)':40s} : {enc_time*1000:8.3f} ms")

            # Decryption
            dec_time, _ = timed_func(crypto_manager.decrypt_entry, encrypted, repeats=5)
            results[f"Decrypt {size:4} KB (hybrid RSA+AES)"] = dec_time
            print(f"{f'Decrypt {size:4} KB (hybrid RSA+AES)':40s} : {dec_time*1000:8.3f} ms")

        # ------------------------------------------------------------------
        # 5. Combined encrypt+sign and verify+decrypt (realistic workflow) – average over 5 runs
        # ------------------------------------------------------------------
        plain = generate_test_data(10)   # 10 KB

        enc_sign_time, package = timed_func(crypto_manager.encrypt_and_sign, plain, repeats=5)
        results["Encrypt + Sign (10 KB)"] = enc_sign_time
        print(f"{'Encrypt + Sign (10 KB)':40s} : {enc_sign_time*1000:8.3f} ms")

        verify_dec_time, _ = timed_func(crypto_manager.verify_and_decrypt, package, repeats=5)
        results["Verify + Decrypt (10 KB)"] = verify_dec_time
        print(f"{'Verify + Decrypt (10 KB)':40s} : {verify_dec_time*1000:8.3f} ms")

        # ------------------------------------------------------------------
        # 6. Password hashing (PBKDF2) – average over 20 runs
        # ------------------------------------------------------------------
        salt = os.urandom(16)
        hash_time, _ = timed_func(user_manager._hash_password, "testpassword", salt, repeats=20)
        results["PBKDF2 password hash (100k iterations)"] = hash_time
        print(f"{'PBKDF2 password hash (100k iterations)':40s} : {hash_time*1000:8.3f} ms")

        # ------------------------------------------------------------------
        # 7. Certificate serialisation / export – average over 100 runs
        # ------------------------------------------------------------------
        export_time, _ = timed_func(key_manager.export_certificate_pem, repeats=100)
        results["Export certificate to PEM"] = export_time
        print(f"{'Export certificate to PEM':40s} : {export_time*1000:8.3f} ms")

        # ------------------------------------------------------------------
        # 8. Diary storage: save & load entry (disk I/O) – average over 10 runs
        # ------------------------------------------------------------------
        diary = DiaryStorage(user_dir=user_manager.get_user_dir("perf_test_user"))
        encrypted_sample = crypto_manager.encrypt_entry(generate_test_data(1))

        # Save
        save_time, entry_id = timed_func(diary.save_entry, "Performance Test", encrypted_sample, repeats=10)
        results["Save diary entry (JSON write)"] = save_time
        print(f"{'Save diary entry (JSON write)':40s} : {save_time*1000:8.3f} ms")

        # Load
        load_time, _ = timed_func(diary.load_entry, entry_id, repeats=10)
        results["Load diary entry (JSON read)"] = load_time
        print(f"{'Load diary entry (JSON read)':40s} : {load_time*1000:8.3f} ms")

    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir, ignore_errors=True)
        print(f"\nCleaned up temporary directory.")


if __name__ == "__main__":
    run_performance_tests()
