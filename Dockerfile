ARG TELEGRAM_TOKEN
FROM python:3.7-buster

WORKDIR /code

COPY requirements.txt .

RUN pip install numpy pandas holidays lunarcalendar tqdm pystan && pip install --no-cache-dir -r requirements.txt

COPY . .


RUN echo $TELEGRAM_TOKEN
ADD . $TELEGRAM_TOKEN

ENTRYPOINT [ "/code/docker-entrypoint.sh" ]