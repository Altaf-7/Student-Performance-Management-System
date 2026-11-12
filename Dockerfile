FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy Django project
COPY AcadTrack/ .

# Collect static files for WhiteNoise
RUN python manage.py collectstatic --noinput

EXPOSE 8000

# Initialize SQLite database and start Gunicorn
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn AcadTrack.wsgi:application --bind 0.0.0.0:8000"]

