# SpendSense 💰

**SpendSense** is a web application for budget and expense tracking, built with Django and powered by MongoDB and Redis. It uses Docker for easy setup and deployment, making it simple to manage your finances.

## ✨ Features

- Track income and expenses
- Categorize transactions
- View budget summaries and insights
- MongoDB for data storage
- Redis for caching and performance
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
git clone https://github.com/HappyMaxxx/SpendSense.git spendsense
cd spendsense
```

### 2. Configure Environment Variables

Create a `.env` file in the project root and add the following:

```env
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1
```

> **Note**: Generate a secure `DJANGO_SECRET_KEY` (e.g., using `python -c "import secrets; print(secrets.token_hex(32))"`). Optionally, add your local network IP (e.g., `192.168.1.6`) to `ALLOWED_HOSTS` to access the app from other devices on your network.

### 3. Collect Static Files

Prepare static assets for production:


```bash
python3 manage.py collectstatic # for Linux/macOS

python manage.py collectstatic # for Windows
```

### 4. Build and Run with Docker

Build the Docker images and start the Django, MongoDB, and Redis containers:

```bash
docker-compose up --build
```

> **Note**: On Linux, you may need `sudo` depending on your Docker setup. On Windows, use Docker Desktop and run the command in PowerShell or CMD.

The application will be available at: [http://localhost:8000](http://localhost:8000).

## 🛑 Stopping and Cleaning Up

### Stop the Containers

To stop the running containers:

```bash
docker-compose down
```

### Remove Containers and Volumes
To stop containers and remove them along with the MongoDB data volume:

```bash
docker-compose down -v
```

> **Warning**: The `-v` flag deletes the MongoDB database volume, resulting in data loss. Use with caution.

> **Important**: After removing the MongoDB volume, the Django superuser account will be deleted. Create a new superuser by running:
> ```bash
> docker-compose run web python manage.py createsuperuser
> ```
> Follow the prompts to set up a new admin account for accessing the Django admin panel.

## 🐳 Docker Compose Configuration

The `docker-compose.yml` defines three services:

- **web**: The Django application, built from the project directory, exposed on port `8000`.
- **db**: MongoDB, using the `mongo:latest` image, with data persisted in the `mongo_data` volume, exposed on port `27017`.
- **redis**: Redis, using the `redis:latest` image, exposed on port `6379`.

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
      - DATABASE_URL=mongodb://db:27017/finance_tracker
  db:
    image: mongo:latest
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db
  redis:
    image: redis:latest
    ports:
      - "6379:6379"
volumes:
  mongo_data:
```

## 🔧 Troubleshooting

- **Port conflicts**: Ensure ports `8000`, `27017`, and `6379` are free. Check with `sudo netstat -tuln | grep <port>`.
- **MongoDB connection issues**: Verify the `DATABASE_URL` in the `.env` file matches the MongoDB service name (`db`) and database name (`finance_tracker`).
- **Docker permissions**: On Linux, if you encounter permission errors, add your user to the Docker group: `sudo usermod -aG docker $USER`.

## 🌐 Accessing from Local Network

To access **SpendSense** from another device on your local network:

1. Add your machine’s local IP (e.g., `192.168.1.6`) to `ALLOWED_HOSTS` in the `.env` file.
2. Ensure your firewall allows traffic on port `8000`.
3. Access the app via `http://<your-ip>:8000` from another device.

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🙌 Contributing

Contributions are welcome! Please open an issue or submit a pull request on GitHub.

---

Happy budgeting with **SpendSense**! 💸