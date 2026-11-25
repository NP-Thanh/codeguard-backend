
from urllib.parse import urlparse

from redis.cluster import RedisCluster

from app.core.config import settings


_redis_client: RedisCluster | None = None


def get_redis() -> RedisCluster:
    global _redis_client

    if _redis_client is None:
        parsed_url = urlparse(settings.redis_url)

        is_local_tunnel = parsed_url.hostname in {
            "127.0.0.1",
            "localhost",
        }

        redis_options = {
            "decode_responses": True,
            "ssl_cert_reqs": "required",
            "socket_connect_timeout": 10,
            "socket_timeout": 10,
        }

        if is_local_tunnel:
            tunnel_port = parsed_url.port or 6380

            def remap_address(address):
                return ("127.0.0.1", tunnel_port)

            redis_options["address_remap"] = remap_address
            redis_options["ssl_check_hostname"] = False

        _redis_client = RedisCluster.from_url(
            settings.redis_url,
            **redis_options,
        )

    return _redis_client


def blacklist_token(jti: str, ttl_seconds: int) -> None:
    if ttl_seconds <= 0:
        return

    client = get_redis()
    client.setex(f"blacklist:{jti}", ttl_seconds, "1")


def is_token_blacklisted(jti: str) -> bool:
    client = get_redis()
    return client.exists(f"blacklist:{jti}") == 1


def close_redis() -> None:
    global _redis_client

    if _redis_client is not None:
        _redis_client.close()
        _redis_client = None
