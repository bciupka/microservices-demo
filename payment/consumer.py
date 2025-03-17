import time
from redis_om import get_redis_connection
from main import Order

key = "order_refund"
group = "payment_group"

redis_streams = get_redis_connection(decode_responses=True, db=2)

# try:
#     stream_info = redis_streams.xinfo_stream(key)
#     print(f"Stream exists: {key}")
# except Exception:
#     redis_streams.xadd(key, {"dummy": "val"}, id="0-1")
#     redis_streams.xdel(key, "0-1")
#     print("Created stream")

try:
    redis_streams.xgroup_create(key, group, mkstream=True)
    print("Group created")
except Exception as e:
    print(e)

while True:
    try:
        result = redis_streams.xreadgroup(group, "payment_consumer", {key: ">"})
        if result != []:
            for i in result:
                messages = i[1]
                stream_id = messages[0][0]
                obj = messages[0][1]
                order = Order.get(obj["pk"])
                order.status = "refund"
                order.save()
                redis_streams.xack(key, group, stream_id)
    except Exception as e:
        print(e)

    time.sleep(3)
