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
redis = get_redis_connection(decode_responses=True, db=0)  # 0-15 for one container


class ProductInput(BaseModel):
    name: str
    price: float
    quantity: int


class ProductOutput(ProductInput):
    id: str


class Product(HashModel):
    name: str
    price: float
    quantity: int

    class Meta:
        database = redis


Migrator().run()


def format(pk):
    result = Product.get(pk)
    model = ProductOutput(
        id=pk, name=result.name, price=result.price, quantity=result.quantity
    )
    return model


@app.get("/")
async def test():
    return "Ready!"


@app.get("/products")
def list_products():
    return [format(i) for i in Product.all_pks()]


@app.get("/products/{pk}")
def get_product(pk: str):
    return Product.get(pk)


@app.post("/products/add")
def add_product(product_input: ProductInput):
    product = Product(
        name=product_input.name,
        price=product_input.price,
        quantity=product_input.quantity,
    )
    return product.save()


@app.delete("/products/{pk}")
def delete_product(pk: str):
    return Product.delete(pk)
