import redis


def get_redis_db():
    return redis.Redis(host='redis', port=6379, db=0)


def normalize_timestamp(t):
    # 10000 miliseconds -> 10s
    return int(t / 10000) * 10000
