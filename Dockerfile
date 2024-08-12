FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1


WORKDIR /photoshare-app

ENV PYTHONPATH=/photoshare-app

COPY requirements.txt .

COPY . /photoshare-app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

WORKDIR /photoshare-app/app

CMD [ "python", "main.py" ]