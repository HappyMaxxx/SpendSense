## 📚 API Documentation

**SpendSense** provides a RESTful API built with Django REST Framework (DRF) for managing user accounts, transactions, and categories. The API requires authentication via a token, which can be obtained from the user's profile in the application.

### Authentication

All API requests must include an `Authorization` header with a Token:

```
Authorization: Token <your-api-token>
```

To obtain an API token:
1. Log in to the **SpendSense** application.
2. Navigate to the API settings page (`/link_api/`) and generate or retrieve your API token.
3. Alternatively, use the `/api/v1/token/` endpoint to obtain a token by providing username and password.

### Endpoints

#### 1. Obtain API Token

- **URL**: `/api/v1/token/`
- **Method**: `POST`
- **Description**: Generates an API token for the authenticated user by providing username and password.
- **Request Body**:
  ```json
  {
    "username": "<username>",
    "password": "<password>"
  }
  ```
- **Response**:
  - **Success (200)**:
    ```json
    {
      "token": "<your-api-token>"
    }
    ```
  - **Error (400)**:
    ```json
    {
      "non_field_errors": ["Unable to log in with provided credentials."]
    }
    ```

#### 2. Check API Token

- **URL**: `/api/v1/token/check/`
- **Method**: `GET`
- **Description**: Validates the provided API token and returns the associated username if valid.
- **Response**:
  - **Success (200)**:
    ```json
    {
      "status": "valid",
      "user": "<username>"
    }
    ```
  - **Error (401)**:
    ```json
    {
      "detail": "Authentication credentials were not provided."
    }
    ```
    ```json
    {
      "detail": "Invalid token."
    }
    ```

#### 3. Get User Accounts

- **URL**: `/api/v1/accounts/`
- **Method**: `GET`
- **Description**: Retrieves a list of accounts and their balances for the authenticated user.
- **Response**:
  - **Success (200)**:
    ```json
    {
      "user": "<username>",
      "accounts": [
        {
          "name": "<account_name>",
          "balance": <balance>
        },
        ...
      ]
    }
    ```
  - **Error (401)**:
    ```json
    {
      "detail": "Authentication credentials were not provided."
    }
    ```
    ```json
    {
      "detail": "Invalid token."
    }
    ```
  - **Error (404)**:
    ```json
    {
      "error": "Accounts cannot be found"
    }
    ```

#### 4. Create Account

- **URL**: `/api/v1/accounts/create/`
- **Method**: `GET`
- **Description**: Creates a new account for the authenticated user.
- **Query Parameters**:
  - `account` (string, required): Name of the account.
  - `amount` (float, optional): Initial balance of the account. Defaults to 0 if not provided.
- **Response**:
  - **Success (200)**:
    ```json
    {
      "status": "ok"
    }
    ```
  - **Error (400)**:
    ```json
    {
      "error": "account parameter is required"
    }
    ```
    ```json
    {
      "error": "Invalid amount format. Must be a number."
    }
    ```
  - **Error (401)**:
    ```json
    {
      "detail": "Authentication credentials were not provided."
    }
    ```
    ```json
    {
      "detail": "Invalid token."
    }
    ```
  - **Error (500)**:
    ```json
    {
      "error": "<error_message>"
    }
    ```

#### 5. Get User Transactions

- **URL**: `/api/v1/transactions/`
- **Method**: `GET`
- **Description**: Retrieves transactions for the authenticated user, optionally filtered by date range.
- **Query Parameters**:
  - `from` (string, optional): Start date in ISO 8601 format (e.g., `2024-06-01T00:00:00`). Defaults to 30 days ago.
  - `to` (string, optional): End date in ISO 8601 format (e.g., `2024-06-30T23:59:59`). Defaults to current date.
- **Response**:
  - **Success (200)**:
    ```json
    {
      "user": "<username>",
      "transactions": [
        {
          "type": "spent" | "earn",
          "amount": <amount>,
          "category": "<category_value>",
          "description": "<description>",
          "account": "<account_name>",
          "time_create": "<ISO8601_timestamp>",
          "time_update": "<ISO8601_timestamp>"
        },
        ...
      ]
    }
    ```
  - **Error (400)**:
    ```json
    {
      "error": "Invalid date format. Use ISO 8601 (e.g., 2024-06-01T00:00:00)"
    }
    ```
  - **Error (401)**:
    ```json
    {
      "detail": "Authentication credentials were not provided."
    }
    ```
    ```json
    {
      "detail": "Invalid token."
    }
    ```
  - **Error (404)**:
    ```json
    {
      "error": "Transactions cannot be found"
    }
    ```

#### 6. Create Transaction

- **URL**: `/api/v1/transactions/create/`
- **Method**: `GET`
- **Description**: Creates a new income or expense transaction for the authenticated user.
- **Query Parameters**:
  - `account` (string, required): Name of the account.
  - `category` (string, required): Value of the category.
  - `amount` (float, required): Amount of the transaction.
  - `type` (string, required): Transaction type, must be either `"spent"` or `"earn"`.
- **Response**:
  - **Success (200)**:
    ```json
    {
      "status": "ok"
    }
    ```
  - **Error (400)**:
    ```json
    {
      "error": "The type parameter must be either \"spent\" or \"earn\"!"
    }
    ```
    ```json
    {
      "error": "<validation_error_message>"
    }
    ```
  - **Error (401)**:
    ```json
    {
      "detail": "Authentication credentials were not provided."
    }
    ```
    ```json
    {
      "detail": "Invalid token."
    }
    ```
  - **Error (404)**:
    ```json
    {
      "error": "Account not found!"
    }
    ```
    ```json
    {
      "error": "Category not found!"
    }
    ```
  - **Error (500)**:
    ```json
    {
      "error": "<error_message>"
    }
    ```

#### 7. Get Categories

- **URL**: `/api/v1/categories/`
- **Method**: `GET`
- **Description**: Retrieves categories available to the authenticated user, optionally filtered by type or user-specific categories.
- **Query Parameters**:
  - `type` (string, optional): Filter by category type (`spent`, `earn`, or omit for all).
  - `user` (string, optional): Filter by user-specific categories (`true` for only user categories, `false` for only system categories, or omit for both).
- **Response**:
  - **Success (200)**:
    ```json
    {
      "user": "<username>",
      "categories": [
        {
          "name": "<category_name>",
          "value": "<category_value>",
          "icon": "<category_icon>",
          "type": "spent" | "earn"
        },
        ...
      ]
    }
    ```
  - **Error (400)**:
    ```json
    {
      "error": "Invalid type parameter. Must be \"spent\", \"earn\", or omitted."
    }
    ```
  - **Error (401)**:
    ```json
    {
      "detail": "Authentication credentials were not provided."
    }
    ```
    ```json
    {
      "detail": "Invalid token."
    }
    ```
  - **Error (404)**:
    ```json
    {
      "error": "Categories cannot be found"
    }
    ```

#### 8. Create Category

- **URL**: `/api/v1/categories/create/`
- **Method**: `GET`
- **Description**: Creates a new income or expense category for the authenticated user.
- **Query Parameters**:
  - `name` (string, required): Name of the new category.
  - `icon` (string, required): Emoji or icon for the category (must be a single valid emoji).
  - `type` (string, required): Category type, must be either `"spent"` or `"earn"`.
- **Response**:
  - **Success (200)**:
    ```json
    {
      "status": "ok"
    }
    ```
  - **Error (400)**:
    ```json
    {
      "error": "The type parameter must be either \"spent\" or \"earn\"!"
    }
    ```
    ```json
    {
      "error": "Icon must be a single valid emoji."
    }
    ```
    ```json
    {
      "error": "<validation_error_message>"
    }
    ```
  - **Error (401)**:
    ```json
    {
      "detail": "Authentication credentials were not provided."
    }
    ```
    ```json
    {
      "detail": "Invalid token."
    }
    ```
  - **Error (500)**:
    ```json
    {
      "error": "<error_message>"
    }
    ```

#### 9. Get Profile Data

- **URL**: `/api/v1/profile-data/`
- **Method**: `GET`
- **Description**: Retrieves the authenticated user's total spending, total earnings, and the difference between earnings and spending.
- **Response**:
  - **Success (200)**:
    ```json
    {
      "user": "<username>",
      "total_all_spending": <total_spending>,
      "total_all_earning": <total_earning>,
      "total_all_diff": <total_earning - total_spending>
    }
    ```
  - **Error (400)**:
    ```json
    {
      "error": "<error_message>"
    }
    ```
  - **Error (401)**:
    ```json
    {
      "detail": "Authentication credentials were not provided."
    }
    ```
    ```json
    {
      "detail": "Invalid token."
    }
    ```

### Example Usage

#### Obtain API Token
```bash
curl -X POST -d "username=<username>&password=<password>" http://localhost:8000/api/v1/token/
```

#### Check API Token
```bash
curl -H "Authorization: Token <your-api-token>" http://localhost:8000/api/v1/token/check/
```

#### Get User Accounts
```bash
curl -H "Authorization: Token <your-api-token>" http://localhost:8000/api/v1/accounts/
```

#### Create an Account
```bash
curl -H "Authorization: Token <your-api-token>" http://localhost:8000/api/v1/accounts/create/?account=Main&amount=1000
```

#### Get Transactions for a Date Range
```bash
curl -H "Authorization: Token <your-api-token>" http://localhost:8000/api/v1/transactions/?from=2024-06-01T00:00:00&to=2024-06-30T23:59:59
```

#### Create a Transaction
```bash
curl -H "Authorization: Token <your-api-token>" http://localhost:8000/api/v1/transactions/create/?type=spent&account=Main&category=supermarket&amount=150
```

#### Get Categories
```bash
curl -H "Authorization: Token <your-api-token>" http://localhost:8000/api/v1/categories/?type=spent&user=true
```

#### Create a Category
```bash
curl -H "Authorization: Token <your-api-token>" http://localhost:8000/api/v1/categories/create/?type=spent&name=Groceries&icon=🛒
```

#### Get Profile Data
```bash
curl -H "Authorization: Token <your-api-token>" http://localhost:8000/api/v1/profile-data/
```

## 🛠️ API Client

For easier interaction with the **SpendSense** API, you can use the dedicated [SpendSense-API-Client](https://github.com/HappyMaxxx/SpendSense-API-Client). This helper program simplifies making API requests to manage your budgets, transactions, and other features programmatically.

- **Repository**: [https://github.com/HappyMaxxx/SpendSense-API-Client](https://github.com/HappyMaxxx/SpendSense-API-Client)
- **Features**: 
  - Simplified API calls for creating, updating, and retrieving financial data via DRF endpoints.
  - Command-line interface for quick access to SpendSense functionality.
  - Well-documented examples to get started.

Check the repository for setup instructions and usage details.