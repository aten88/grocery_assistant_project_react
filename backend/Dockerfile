FROM python:3.9-slim

WORKDIR /app

RUN pip install gunicorn==20.1.0

COPY requirements.txt ./
COPY /.env /app/.env


RUN pip install -r requirements.txt --no-cache-dir
RUN pip install python-dotenv

COPY ./ ./

# CMD ["python", "manage.py", "runserver", "0:8000"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "foodgram.wsgi"]
