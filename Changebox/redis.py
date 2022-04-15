import redis

REDIS_HOST = '127.0.0.1'
REDIS_PORT = '6379'

redis_queue = redis.Redis(host=REDIS_HOST, port=int(REDIS_PORT), db=0)
redis_money = redis.Redis(host=REDIS_HOST, port=int(REDIS_PORT), db=1)
