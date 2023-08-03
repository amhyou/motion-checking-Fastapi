from redis import from_url

redis_db = from_url("redis://default:fe439bfc1f534b4d86c9c6c100914fd2@eu1-crack-jawfish-38213.upstash.io:38213")

print(redis_db.get("current_account"))