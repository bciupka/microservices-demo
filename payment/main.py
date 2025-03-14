from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection, HashModel, Migrator
from pydantic import BaseModel

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


class Order(HashModel):
    product_id: str
    price: float
    fee: float
    total: float
    quatity: int
    status: str  # pending / completed / refunded

    class Meta:
        database = redis


Migrator().run()
