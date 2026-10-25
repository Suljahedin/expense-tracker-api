from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import Category, Expense
from schemas.category_schemas import CategoryCreate, CategoryResponse, CategoryUpdate
from schemas.expense_schemas import ExpenseCreate, ExpenseResponse

Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Hello world!"}


# CATEGORIES ENDPOINTS

# Get all of the categories
@app.get("/categories", response_model=list[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()


# Get category with specific ID
@app.get("/categories/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = db.get(Category, category_id)

    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    return category


# Create category
@app.post("/categories", response_model=CategoryResponse, status_code=201)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    new_category = Category(name=category.name)

    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return new_category


# Delete category by ID
@app.delete("/categories/{category_id}", status_code=204)
def delete_category(category_id:int, db: Session = Depends(get_db)):
    category = db.get(Category, category_id)

    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    if db.query(Expense).filter(Expense.category_id == category_id).first():
        raise HTTPException (
            status_code=409,
            detail="Cannot delete category with  existing expenses."
        )

    db.delete(category)
    db.commit()

# Update category by ID
@app.put("/categories/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: Session = Depends(get_db)
):
    category = db.get(Category, category_id)

    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    category.name = data.name
    db.commit()
    db.refresh(category)

    return category


# EXPENSES ENDPOINTS

# Get all expenses
@app.get("/expenses", response_model=list[ExpenseResponse])
def get_expenses(db: Session = Depends(get_db)):
    return db.query(Expense).all()


# Get expense by ID
@app.get("/expenses/{expense_id}", response_model=ExpenseResponse)
def get_expense(expense_id: int, db: Session = Depends(get_db)):
    expense = db.get(Expense, expense_id)

    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")

    return expense


# Create an expense
@app.post("/expenses", response_model=ExpenseResponse, status_code=201)
def create_expense(expense: ExpenseCreate, db: Session = Depends(get_db)):
    category = db.get(Category, expense.category_id)

    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")


    new_expense = Expense(
        title=expense.title,
        amount=expense.amount, 
        date=expense.date, 
        category_id=expense.category_id
    )

    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)

    return new_expense


# Delete an expense by ID
@app.delete("/expenses/{expense_id}", status_code=204)
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    expense = db.get(Expense, expense_id)

    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")

    db.delete(expense)
    db.commit()

# Update an expense by ID
@app.put("/expenses/{expense_id}", response_model=ExpenseResponse)
def update_expense(
    expense_id: int,
    data: ExpenseCreate,
    db: Session = Depends(get_db)
):
    expense = db.get(Expense, expense_id)

    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found.")

    category = db.get(Category, data.category_id)

    if category is None:
        raise HTTPException(status_code=404, detail="Category not found.")

    expense.title = data.title
    expense.amount = data.amount
    expense.date = data.date
    expense.category_id = data.category_id

    db.commit()
    db.refresh(expense)

    return expense