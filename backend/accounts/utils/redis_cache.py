from django.core.cache import cache

def store_otp(email, otp):
    cache_key = f"otp:{email}"
    cache.set(cache_key, otp, timeout=300)


def verify_otp(email, user_otp):
    cache_key = f"otp:{email}"
    stored_otp = cache.get(cache_key)

    if not stored_otp:
        return False, "OTP expired or not found"

    if str(stored_otp) != str(user_otp):
        return False, "Invalid OTP"

    cache.delete(cache_key)

    return True, "OTP verified"