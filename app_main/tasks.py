from Changebox.celery import app
from app_main.lib.set_all_rates import set_all_rates


@app.task(time_limit=2)
def clear_redis():
    from Changebox.redis import redis_queue
    redis_queue.flushdb()


@app.task(time_limit=25, soft_time_limit=20)
def set_rates():
    set_all_rates()
