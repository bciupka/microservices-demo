import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.background import BackgroundTasks
from redis_om import get_redis_connection, HashModel, Migrator
from pydantic import BaseModel
import requests

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_headers=["*"],
    allow_methods=["*"],
)

# redis = get_redis_connection(host="", port=6379, password="", decode_responses=True)
redis = get_redis_connection(decode_responses=True, db=1)  # 0-15 for one container
redis_streams = get_redis_connection(decode_responses=True, db=2)


class OrderCreate(BaseModel):
    product_id: str
    quantity: int


class Order(HashModel):
    product_id: str
    price: float
    fee: float
    total: float
    quantity: int
    status: str  # pending / completed / refunded

    class Meta:
        database = redis


# Redis indexing works only for db0 (redis-om limitation)
# Migrator().run()


def order_completed(order: Order):
    time.sleep(7)
    order.status = "completed"
    order.save()
    redis_streams.xadd("order_completed", order.model_dump(), "*")


@app.post("/orders", status_code=201)
async def create_order(body: OrderCreate, background_tasks: BackgroundTasks):
    product = requests.get(f"http://localhost:8000/products/{body.product_id}")
    product_json = product.json()
    order = Order(
        product_id=body.product_id,
        price=product_json["price"],
        fee=0.2 * product_json["price"],
        total=1.2 * product_json["price"] * body.quantity,
        quantity=body.quantity,
        status="pending",
    )

    order.save()
    background_tasks.add_task(order_completed, order)
    return order


@app.get("/orders/{pk}")
def get_order(pk: str):
    return Order.get(pk)
