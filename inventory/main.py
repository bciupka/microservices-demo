from fastapi import FastAPI
from redis_om import get_redis_connection, HashModel


app = FastAPI()


redis_conn = get_redis_connection(decode_responses=True)


class Product(HashModel):
    name: str
    price: float
    qty: int

    class Meta:
        database = redis_conn


@app.post("/product")
async def post_product(product: Product):
    product.save()
    return product


@app.get("/products")
async def list_products():
    return Product.all_pks()
