FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt ./
COPY /.env /app/.env


RUN pip install -r requirements.txt --no-cache-dir
RUN pip install python-dotenv

COPY ./ ./

CMD ["python", "manage.py", "runserver", "0:8000"]
