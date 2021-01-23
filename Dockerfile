FROM python:3.7-slim-stretch

WORKDIR /code

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT [ "/code/docker-entrypoint.sh" ]