## 📚 API Documentation

**SpendSense** provides an internal API for accessing user accounts, transactions, and categories. The API requires authentication via a Bearer token, which can be obtained from the user's profile in the application.

### Authentication

All API requests must include an `Authorization` header with a Bearer token:

```
Authorization: Bearer <your-api-token>
```

To obtain an API token:
1. Log in to the **SpendSense** application.
2. Navigate to the API settings page (`/link_api/`) and generate or retrieve your API token.

### Endpoints

#### 1. Check API Token

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
      "error": "Token not given"
    }
    ```
    ```json
    {
      "error": "Token must start with Bearer"
    }
    ```
    ```json
    {
      "error": "Invalid token"
    }
    ```

#### 2. Get User Accounts

- **URL**: `/api/v1/accounts/`
- **Method**: `GET`
- **Description**: Retrieves a list of accounts for the authenticated user.
- **Response**:
  - **Success (200)**:
    ```json
    {
      "user": "<username>",
      "accounts": [
        {
          "account": "<account_name>",
          "balance": <balance>
        },
        ...
      ]
    }
    ```
  - **Error (401)**:
    ```json
    {
      "error": "Token not given"
    }
    ```
    ```json
    {
      "error": "Token must start with Bearer"
    }
    ```
    ```json
    {
      "error": "Invalid token"
    }
    ```
    ```json
    {
      "error": "Accounts cannot be found"
    }
    ```

#### 3. Get User Transactions

- **URL**: `/api/v1/transactions/`
- **Method**: `GET`
- **Description**: Retrieves transactions for the authenticated user, optionally filtered by date range.
- **Query Parameters**:
  - `from`: Start date in ISO 8601 format (e.g., `2024-06-01T00:00:00`). Defaults to 30 days ago.
  - `to`: End date in ISO 8601 format (e.g., `2024-06-30T23:59:59`). Defaults to current date.
- **Response**:
  - **Success (200)**:
    ```json
    {
      "user": "<username>",
      "transactions": [
        {
          "type": "spent" | "earn",
          "amount": <amount>,
          "category": "<category_name>",
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
      "error": "Token not given"
    }
    ```
    ```json
    {
      "error": "Token must start with Bearer"
    }
    ```
    ```json
    {
      "error": "Invalid token"
    }
    ```
  - **Error (404)**:
    ```json
    {
      "error": "Transactions cannot be found"
    }
    ```

#### 4. Get Categories

- **URL**: `/api/v1/categories/get/`
- **Method**: `GET`
- **Description**: Retrieves categories available to the authenticated user, optionally filtered by type or user-specific categories.
- **Query Parameters**:
  - `type`: Filter by category type (`spent`, `earn`, or omit for all).
  - `user`: Filter by user-specific categories (`true` for only user categories, `false` for only system categories, or omit for both).
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
          "type": "spent" | "earn",
          "transaction_name": "<transaction_name>"
        },
        ...
      ]
    }
    ```
  - **Error (400)**:
    ```json
    {
      "error": "Invalid type parameter. Must be 'spent', 'earn', or omitted."
    }
    ```
  - **Error (401)**:
    ```json
    {
      "error": "Token not given"
    }
    ```
    ```json
    {
      "error": "Token must start with Bearer"
    }
    ```
    ```json
    {
      "error": "Invalid token"
    }
    ```
  - **Error (404)**:
    ```json
    {
      "error": "Categories cannot be found"
    }
    ```

#### 5. Get Profile Data

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
      "error": "Token not given"
    }
    ```
    ```json
    {
      "error": "Token must start with Bearer"
    }
    ```
    ```json
    {
      "error": "Invalid token"
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
      "error": "The type parameter must be either “spent” or “earn”!"
    }
    ```
    ```json
    {
      "error": "A problem occurred while creating a transaction."
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
      "error": "Token not given"
    }
    ```
    ```json
    {
      "error": "Token must start with Bearer"
    }
    ```
    ```json
    {
      "error": "Invalid token"
    }
    ```
  - **Error (404)**:
    ```json
    {
      "error": "Category not found!"
    }
    ```
    ```json
    {
      "error": "Account not found!"
    }
    ```

### Example Usage

#### Check API Token
```bash
curl -H "Authorization: Bearer <your-api-token>" http://localhost:8000/api/v1/token/check/
```

#### Get User Accounts
```bash
curl -H "Authorization: Bearer <your-api-token>" http://localhost:8000/api/v1/accounts/
```

#### Get Transactions for a Date Range
```bash
curl -H "Authorization: Bearer <your-api-token>" http://localhost:8000/api/v1/transactions/?from=2024-06-01T00:00:00&to=2024-06-30T23:59:59
```

#### Get Categories
```bash
curl -H "Authorization: Bearer <your-api-token>" http://localhost:8000/api/v1/categories/get/?type=spent&user=true
```

##### Get Profile Data
```bash
curl -H "Authorization: Bearer <your-api-token>" http://localhost:8000/api/v1/profile-data/
```

##### Сreate a Transaction
```bash
curl -H "Authorization: Bearer <your-api-token>" http://localhost:8000/api/v1/transactions/create/?type=spent&account=Main&category=supermarket&amount=150
```