import json
import redis
from chatup_chat.config import config, ENV, hostname


def get_redis_client():
    cache = redis.Redis(host=config.redis_cluster.url, port=config.redis_cluster.port)
    cache.ping()
    return cache


class RedisCluster:
    def __init__(self) -> None:
        self._cache = get_redis_client()
        self.namespace = f"{hostname}-{ENV}"
        self.TIMEOUT_SECONDS = 7200  # 2 hours

    def __setitem__(self, key, value):
        self._cache.set(self.get_namespaced_key(key), value, ex=self.TIMEOUT_SECONDS)

    def __getitem__(self, key):
        return self.get(key)

    def get_raw(self, key):
        return self._cache.get(key)

    def get(self, key):
        return self._cache.get(self.get_namespaced_key(key))

    def hget(self, name, key):
        return self._cache.hget(self.get_namespaced_key(name), key)

    def hset(self, name, key, value):
        name = self.get_namespaced_key(name)
        self._cache.hset(name, key, value)
        self._cache.expire(name, self.TIMEOUT_SECONDS)

    def hkeys(self, name):
        return self._cache.hkeys(self.get_namespaced_key(name))

    def __contains__(self, key):
        if self._cache.get(self.get_namespaced_key(key)) is not None:
            return True
        return False

    def get_namespaced_key(self, key):
        return f"chatup_chat_{self.namespace}_{key}"


class RedisClusterJson(RedisCluster):
    def __init__(self) -> None:
        super().__init__()

    def __setitem__(self, key, value):
        super(RedisClusterJson, self).__setitem__(key, json.dumps(value).encode("utf-8"))

    def get(self, key):
        value = super(RedisClusterJson, self).get(key)
        if not value:
            return None
        return json.loads(value.decode("utf-8"))

    def get_with_whole_key(self, key):
        value = super(RedisClusterJson, self).get_raw(key)
        if not value:
            return None
        return json.loads(value.decode("utf-8"))

    def get_by_patterns(self, key):
        keys = self.get_keys(pattern=key)
        results = [self.get_with_whole_key(the_key.decode("utf-8")) for the_key in keys]
        return results

    def hget(self, name, key):
        value = super(RedisClusterJson, self).hget(name, key)
        if value is None:
            return None
        return json.loads(value.decode("utf-8"))

    def hset(self, name, key, value):
        super(RedisClusterJson, self).hset(name, key, json.dumps(value).encode("utf-8"))

    def clear_cache(self, pattern=""):
        keys = self.get_keys(pattern)
        if keys:
            self._cache.delete(*keys)

    def get_keys(self, pattern=""):
        all_keys = []
        cursor, keys = self._cache.scan(match=f"{self.get_namespaced_key(pattern)}*")
        all_keys.extend(keys)
        while cursor != 0:
            cursor, keys = self._cache.scan(match=f"{self.get_namespaced_key(pattern)}*", cursor=cursor)
            all_keys.extend(keys)
        return all_keys
