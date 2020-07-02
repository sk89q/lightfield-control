FROM python:3.8-buster

RUN apt-get update
RUN pip install pipenv

RUN mkdir /data

WORKDIR lfcontrol

COPY Pipfile .
COPY Pipfile.lock .
RUN pipenv install --dev --deploy --system

COPY . .

CMD ["python", "./lightfield-control.py", "run"]
