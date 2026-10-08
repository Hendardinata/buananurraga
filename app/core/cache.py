import time
from functools import wraps

def ttl_cache(ttl_seconds):
    """
    Simple in-memory TTL cache decorator for functions without external dependencies.
    Caches function return values for `ttl_seconds`.
    """
    def decorator(func):
        cache = {}
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create a string key from args and kwargs
            key = str(args) + str(kwargs)
            now = time.time()
            
            # Check if key is in cache and hasn't expired
            if key in cache:
                result, timestamp = cache[key]
                if now - timestamp < ttl_seconds:
                    return result
                    
            # Not in cache or expired, call function
            result = func(*args, **kwargs)
            cache[key] = (result, now)
            return result
            
        def clear_cache():
            cache.clear()
            
        wrapper.clear_cache = clear_cache
        return wrapper
    return decorator
