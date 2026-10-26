# Expense Tracker API

A RESTful API for managing personal finances, built with FastAPI, SQLAlchemy, and SQLite.

## Features

- Create, retrieve, update, and delete expense categories
- Create, retrieve, update, and delete financial transactions
- Support for income and expense transactions
- Filter transactions by category, date range, and transaction type
- Paginate transaction results
- Calculate total income, total expenses, and balance
- Validate request data with Pydantic
- Use SQLAlchemy ORM for database operations
- Return appropriate HTTP status codes for common errors

## Tech Stack

- **Python**
- **FastAPI** — API framework
- **Pydantic** — request validation and response schemas
- **SQLAlchemy** — ORM and database queries
- **SQLite** — database
- **uv** — Python project and dependency management

## Requirements

- Python version compatible with the project configuration
- [uv](https://docs.astral.sh/uv/)

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Suljahedin/expense-tracker-api.git
cd expense-tracker-api
```

### 2. Install dependencies

```bash
uv sync
```

### 3. Start the development server

```bash
uv run fastapi dev main.py
```

### 4. Open the API documentation

Visit:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## API Endpoints

### Categories

| Method | Endpoint                    | Description          |
| ------ | --------------------------- | -------------------- |
| GET    | `/categories`               | Get all categories   |
| GET    | `/categories/{category_id}` | Get a category by ID |
| POST   | `/categories`               | Create a category    |
| PUT    | `/categories/{category_id}` | Update a category    |
| DELETE | `/categories/{category_id}` | Delete a category    |

### Expenses and Income

| Method | Endpoint                 | Description                                           |
| ------ | ------------------------ | ----------------------------------------------------- |
| GET    | `/expenses`              | Get transactions with optional filters and pagination |
| GET    | `/expenses/{expense_id}` | Get a transaction by ID                               |
| POST   | `/expenses`              | Create a transaction                                  |
| PUT    | `/expenses/{expense_id}` | Update a transaction                                  |
| DELETE | `/expenses/{expense_id}` | Delete a transaction                                  |

### Statistics

| Method | Endpoint      | Description                             |
| ------ | ------------- | --------------------------------------- |
| GET    | `/statistics` | Get total income, expenses, and balance |

## Filtering and Pagination

The `GET /expenses` endpoint supports these query parameters:

- `category_id` — filter by category
- `start_date` — include transactions on or after this date
- `end_date` — include transactions on or before this date
- `transaction_type` — `income` or `expense`
- `skip` — number of records to skip
- `limit` — number of records to return, up to 100

Example:

```http
GET /expenses?transaction_type=expense&start_date=2026-10-01&end_date=2026-10-31&skip=0&limit=10
```

## Example Request

Create an expense:

```json
{
  "title": "Groceries",
  "amount": "45.50",
  "date": "2026-10-26",
  "category_id": 1,
  "transaction_type": "expense"
}
```

Create an income:

```json
{
  "title": "Monthly salary",
  "amount": "1500.00",
  "date": "2026-10-26",
  "category_id": 2,
  "transaction_type": "income"
}
```

## Database

The application uses a local SQLite database. The database file is created locally and should not be committed to version control.

## License

No license has been specified yet.
