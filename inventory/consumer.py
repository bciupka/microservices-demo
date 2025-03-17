import time
from redis_om import get_redis_connection
from main import Product

key = "order_completed"
group = "inventory_group"

redis_streams = get_redis_connection(decode_responses=True, db=2)

try:
    redis_streams.xgroup_create(key, group, mkstream=True)
    print("Group created")
except Exception as e:
    print(e)

while True:
    try:
        result = redis_streams.xreadgroup(group, key, {key: ">"})
        if result != []:
            for i in result:
                obj = i[1][0][1]
                product = Product.get(obj["product_id"])
                product.quantity = max(0, product.quantity - int(obj["quantity"]))
                product.save()
                print(product)
    except Exception as e:
        print(e)

    time.sleep(3)
