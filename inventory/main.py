from fastapi import FastAPI
from redis_om import get_redis_connection, HashModel
from starlette.requests import Request
from starlette.responses import Response


app = FastAPI()


redis_conn = get_redis_connection(url="redis://localhost:6379", decode_responses=True)


class Product(HashModel):
    name: str
    price: float
    qty: int

    class Meta:
        database = redis_conn


@app.post("/product")
async def post_product(product: Product):
    product.save()
    return "done"


@app.get("/products")
async def list_products(request: Request, response: Response):
    return {"list": Product.all_pks()}
