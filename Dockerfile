FROM python:3.11

RUN mkdir /app

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip
RUN pip install -r /app/requirements.txt

CMD [ "python", "tasks.py" ]