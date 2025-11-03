import os

CACHE_FILE = os.path.join("data", "cache.txt")

def load_cache():
    cache = {}
    if not os.path.exists(CACHE_FILE):
        os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
        return cache
    with open(CACHE_FILE, "r") as file:
        for line in file:
            key, evaluation, must_jump = line.split("|")
            cache[key] = (float(evaluation), must_jump)
    return cache


def save_cache(cache, must_jump):
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, "w") as file:
        for key in cache:
            file.write(f"{key}|{cache[key][0]}|{must_jump}\n")


cache = load_cache()
