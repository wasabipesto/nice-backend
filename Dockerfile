FROM python:3.10-bullseye

ENV PYTHONUNBUFFERED=1

EXPOSE 5000

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "./app.py"]