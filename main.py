from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy import func, case
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import date

from database import Base, engine, get_db
from models import Category, Expense
from schemas.category_schemas import CategoryCreate, CategoryResponse, CategoryUpdate
from schemas.expense_schemas import ExpenseCreate, ExpenseResponse, StatisticsResponse

Base.metadata.create_all(bind=engine)

app = FastAPI()

def commit_or_rollback(db: Session) -> None:
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback
        raise

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
    commit_or_rollback(db)
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
    commit_or_rollback(db)

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
    commit_or_rollback(db)
    db.refresh(category)

    return category


# EXPENSES ENDPOINTS

# Get all expenses, with filtering
@app.get("/expenses", response_model=list[ExpenseResponse])
def get_expenses(
    category_id: int | None = Query(default=None, gt=0),
    start_date: date | None = None,
    end_date: date | None = None,
    transaction_type: str | None = Query(
        default=None,
        pattern="^(income|expense)$",
    ),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=400,
            detail="start_date cannot be after end_date",
        )
    
    query = db.query(Expense)

    if category_id is not None:
        query = query.filter(Expense.category_id == category_id)

    if start_date is not None:
        query = query.filter(Expense.date >= start_date)

    if end_date is not None:
        query = query.filter(Expense.date <= end_date)

    if transaction_type is not None:
        query = query.filter(
            Expense.transaction_type == transaction_type
        )

    return (
        query.order_by(Expense.date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

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
        category_id=expense.category_id,
        transaction_type=expense.transaction_type
    )

    db.add(new_expense)
    commit_or_rollback(db)
    db.refresh(new_expense)

    return new_expense


# Delete an expense by ID
@app.delete("/expenses/{expense_id}", status_code=204)
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    expense = db.get(Expense, expense_id)

    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")

    db.delete(expense)
    commit_or_rollback(db)

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
    expense.transaction_type = data.transaction_type

    commit_or_rollback(db)
    db.refresh(expense)

    return expense

# STATISTICS ENDPOINTS

@app.get("/statistics", response_model=StatisticsResponse)
def get_statistics(db: Session = Depends(get_db)):
    total_income, total_expenses = db.query(
        func.coalesce(
            func.sum(
                case(
                    (Expense.transaction_type == "income", Expense.amount),
                    else_=0,
                )
            ),
            0,
        ),
        func.coalesce(
            func.sum(
                case(
                    (Expense.transaction_type == "expense", Expense.amount),
                    else_=0,
                )
            ),
            0,
        ),
    ).one()

    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "balance": total_income - total_expenses,
    }