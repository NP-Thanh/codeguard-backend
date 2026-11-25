from redis.cluster import RedisCluster

client = RedisCluster.from_url(
    "rediss://codeguard-redis-931pru.serverless.apse2.cache.amazonaws.com:6379",
    ssl_cert_reqs="required",
    decode_responses=True,
    socket_connect_timeout=5,
    socket_timeout=5,
)

try:
    print("PING:", client.ping())

    client.set("codeguard:test", "connected", ex=60)

    print("GET:", client.get("codeguard:test"))

except Exception as e:
    print(type(e).__name__, str(e))

finally:
    client.close()