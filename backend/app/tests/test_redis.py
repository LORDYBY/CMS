import redis

r = redis.Redis.from_url("redis://localhost:6379/0")
r.set("cms_health", "ok")
print(r.get("cms_health").decode())
