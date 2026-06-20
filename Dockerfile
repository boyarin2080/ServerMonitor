# Используем официальный Python образ на базе Alpine (меньший размер)
FROM python:3.11-alpine

# Устанавливаем системные зависимости для psutil
RUN apk update && apk add --no-cache \
    gcc \
    musl-dev \
    linux-headers \
    && rm -rf /var/cache/apk/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY servmon.py .

# Открываем порт для Flask приложения
EXPOSE 5000

# Запускаем приложение
CMD ["python", "servmon.py"]