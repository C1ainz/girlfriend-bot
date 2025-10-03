# Лёгкий официальный образ с корректным Python
FROM python:3.11-slim

# Не буферизуем вывод логов
ENV PYTHONUNBUFFERED=1

# Рабочая папка
WORKDIR /app

# Сначала зависимости (кэш быстрее)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Кладём остальной код
COPY . /app

# Старт
CMD ["python", "main.py"]
