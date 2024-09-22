# Используем slim версию Python 3.12
FROM python:3.12-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем requirements.txt в контейнер
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код бота и .env файл в контейнер
COPY . .

# Запуск скрипта
CMD ["python", "main.py"]
