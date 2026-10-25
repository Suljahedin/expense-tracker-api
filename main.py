from fastapi import FastAPI

from database import Base, engine
from models import Category
from schemas.category_schemas import CategoryCreate, CategoryResponse

app = FastAPI()

categories = []
next_id = 1


@app.get("/")
def root():
    return {"message": "Hello world!"}


@app.get("/categories", response_model=list[CategoryResponse])
def get_categories():
    return categories


@app.post("/categories", response_model=CategoryResponse, status_code=201)
def create_category(category: CategoryCreate):
    global next_id

    new_category = {
        "id": next_id,
        "name": category.name,
    }

    categories.append(new_category)
    next_id += 1

    return new_category
