import time
from redis_om import get_redis_connection
from main import Product

key = "order_completed"
group = "inventory_group"

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
        result = redis_streams.xreadgroup(group, "inventory_consumer", {key: ">"})
        if result != []:
            for i in result:
                messages = i[1]
                stream_id = messages[0][0]
                obj = messages[0][1]
                try:
                    product = Product.get(obj["product_id"])
                    if product.quantity < int(obj["quantity"]):
                        raise Exception("Not enough items to proceed")
                    product.quantity = product.quantity - int(obj["quantity"])
                    product.save()
                except Exception:
                    redis_streams.xadd("order_refund", obj, "*")
                finally:
                    redis_streams.xack(key, group, stream_id)

    except Exception as e:
        print(e)

    time.sleep(3)
