# SpendSense 💰

<p align="center">
  <img src="src/img/logo.png" alt="SpendSense Logo" />
</p>

<p align="center">
  <a href="https://ko-fi.com/v1mer" target="_blank">
    <img src="https://img.shields.io/badge/Support-Ko--fi-FF5E5B?style=flat-square&logo=ko-fi&logoColor=white" alt="Support me on Ko-fi" />
  </a>
  <a href="mailto:mpatik2006@gmail.com">
    <img src="https://img.shields.io/badge/Donate-PayPal-00457C?style=flat-square&logo=paypal&logoColor=white" alt="Donate via PayPal" />
  </a>
</p>

**SpendSense** is a web application for budget and expense tracking, built with Django and powered by PostgreSQL and Redis. It uses Docker for easy setup and deployment, making it simple to manage your finances.

## ✨ Features

- Track income and expenses
- Categorize transactions
- View budget summaries and insights
- Telegram bot for managing transactions and viewing account details (optional, for enhanced interaction)
- PostgreSQL for data storage (previously used MongoDB)
- Redis for caching and performance
- Celery for asynchronous task processing
- Flower for monitoring Celery tasks
- Dockerized setup for consistent environments

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- [Docker](https://www.docker.com/get-started/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [Python 3.10+](https://www.python.org/downloads/) (optional, for manual Django setup)
- [Git](https://git-scm.com/downloads)

## 🚀 Getting Started

Follow these steps to set up and run **SpendSense** on your local machine.

### 1. Clone the Repository

```bash
git clone --depth=1  https://github.com/HappyMaxxx/SpendSense.git spendsense
cd spendsense
```
> **Note**: The `--depth=1` flag performs a shallow clone, downloading only the latest commit to save time and space. If you need the full commit history later, run: 
> ```bash
> git fetch --unshallow
> ```

### 2. Configure Environment Variables

Create a `.env` file in the project root and add the following:

```env
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=web,localhost,127.0.0.1

POSTGRES_DB=app_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

BOT_TOKEN=your-telegram-bot-token-here
BOT_URL='https://t.me/your-bot-name'
```

> **Note**: 
> - Generate a secure `DJANGO_SECRET_KEY` (e.g., using `python -c "import secrets; print(secrets.token_hex(32))"`).
> - The `TELEGRAM_BOT_TOKEN` is optional and only required if you want to use the Telegram bot. Obtain it by creating a bot via [BotFather](https://t.me/BotFather) on Telegram.
> - Optionally, add your local network IP (e.g., `192.168.1.6` or `192.168.0.120`) to `ALLOWED_HOSTS` to access the app from other devices on your network.
### 3. Collect Static Files

Prepare static assets for production:

```bash
python3 manage.py collectstatic # for Linux/macOS
# or
python manage.py collectstatic # for Windows
```

### 4. Build and Run with Docker

Build the Docker images and start the Django, PostgreSQL, Redis, Celery, and Flower containers:

```bash
docker-compose up --build
```

> **Note**: On Linux, you may need `sudo` depending on your Docker setup. On Windows, use Docker Desktop and run the command in PowerShell or CMD.

The application will be available at: [http://localhost:8000](http://localhost:8000).

The Flower dashboard for monitoring Celery tasks will be available at: [http://localhost:5555](http://localhost:5555).

The Telegram bot, if enabled, can be interacted with via Telegram after starting the bot with the provided token.

## 🛑 Stopping and Cleaning Up

### Stop the Containers

To stop the running containers:

```bash
docker-compose down
```

### Remove Containers and Volumes

To stop containers and remove them along with the PostgreSQL data volume:

```bash
docker-compose down -v
```

> **Warning**: The `-v` flag deletes the PostgreSQL database volume, resulting in data loss. Use with caution.

> **Important**: After removing the PostgreSQL volume, the Django superuser account will be deleted. Create a new superuser by running:
> ```bash
> docker-compose run web python manage.py createsuperuser
> ```
> Follow the prompts to set up a new admin account for accessing the Django admin panel.

## 🐳 Docker Compose Configuration

The `docker-compose.yml` defines five services:

- **web**: The Django application, built from the project directory, exposed on port `8000`.
- **db**: PostgreSQL, using the `postgres:15` image, with data persisted in the postgres_data volume, exposed on port `5432`.
- **bot**: The Telegram bot (optional), built from the project directory, running `bot/main.py`, dependent on PostgreSQL, with access to the project directory via a volume. This service only runs if `TELEGRAM_BOT_TOKEN` is provided.
- **redis**: Redis, using the `redis:latest` image, exposed on port `6379`.
- **celery**: Celery worker for asynchronous task processing, built from the project directory, dependent on Redis and PostgreSQL.
- **flower**: Flower dashboard for monitoring Celery tasks, using the `mher/flower` image, exposed on port `5555`.

```yaml
services:
  web:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/app_db
      
    command: ["./wait-for-it.sh", "db:5432", "--", "python3", "manage.py", "runserver", "0.0.0.0:8000"]
  db:
    image: postgres:15
    restart: always
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
  bot:
    build: .
    command: python3 bot/main.py
    volumes:
      - .:/app
    depends_on:
      - db
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/app_db
  redis:
    image: redis:latest
    ports:
      - "6379:6379"
  celery:
    build: .
    command: celery -A spendsense worker --loglevel=info
    depends_on:
      - redis
      - db
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/app_db
  flower:
    image: mher/flower
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
    ports:
      - "5555:5555"
    depends_on:
      - redis
volumes:
  postgres_data:
```

> **Important**: celery and flower services are currently temporarily commented out, as they are not yet in use

## 🔧 Troubleshooting

- **Port conflicts**: Ensure ports `8000`, `27017`, `6379`, and `5555` are free. Check with `sudo netstat -tuln | grep <port>`.
- **PostgreSQL connection issues**: Verify the `DATABASE_URL` in the `.env` file matches the PostgreSQL service name (`db`) and database name (`finance_tracker`).
- **Telegram bot issues**: If using the optional Telegram bot, ensure the `TELEGRAM_BOT_TOKEN` is correctly set in the `.env` file and that the bot is properly registered with BotFather. If the bot fails to start, it will not affect the core web application.
- **Celery issues**: Ensure the `CELERY_BROKER_URL` in the `.env` file is set to `redis://redis:6379/0`.
- **Docker permissions**: On Linux, if you encounter permission errors, add your user to the Docker group: `sudo usermod -aG docker $USER`.

## 🌐 Accessing from Local Network

To access **SpendSense** or the Flower dashboard from another device on your local network:

1. Add your machine’s local IP (e.g., `192.168.1.6` or `192.168.0.120`) to `ALLOWED_HOSTS` in the `.env` file.
2. Ensure your firewall allows traffic on ports `8000` (Django) and `5555` (Flower).
3. Access the app via `http://<your-ip>:8000` or Flower via `http://<your-ip>:5555` from another device.

## 📚 API Documentation

Full API documentation is available in [API.md](./API.md)

## 🛠️ API Client

For easier interaction with the **SpendSense** API, you can use the dedicated [SpendSense-API-Client](https://github.com/HappyMaxxx/SpendSense-API-Client). This helper program simplifies making API requests to manage your budgets, transactions, and other features programmatically.

- **Repository**: [https://github.com/HappyMaxxx/SpendSense-API-Client](https://github.com/HappyMaxxx/SpendSense-API-Client)
- **Features**: 
  - Simplified API calls for creating, updating, and retrieving financial data.
  - Command-line interface for quick access to SpendSense functionality.
  - Well-documented examples to get started.

Check the repository for setup instructions and usage details.

## 🙌 Support the Project

If you find this project useful and would like to support its development, consider donating:

- 💖 Ko-fi: [https://ko-fi.com/v1mer](https://ko-fi.com/v1mer)
- 📬 PayPal: mpatik2006@gmail.com

Your support helps me dedicate more time to improving this project. Thank you! 🙏

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🙌 Contributing

Contributions are welcome! Please open an issue or submit a pull request on GitHub.

---

Happy budgeting with **SpendSense**! 💸