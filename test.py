from redis import from_url

redis_db = from_url("redis://localhost:6379/")

print(redis_db.get("current_account"))