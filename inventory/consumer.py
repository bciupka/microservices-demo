import time
from redis_om import get_redis_connection
from main import Product, redis

key = "order_completed"
group = "inventory_group"

redis_streams = get_redis_connection(decode_responses=True, db=2)

try:
    redis_streams.xgroup_create(key, group)
    print("Group created")
except Exception as e:
    print(e)

while True:
    try:
        result = redis_streams.xreadgroup(group, key, {key: ">"}, None)
        print(result)
    except Exception as e:
        print(e)

    time.sleep(3)
