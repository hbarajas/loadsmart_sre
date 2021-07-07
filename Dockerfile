FROM python:3.8-slim-buster

# add files and install requirements
COPY requirements.txt /app/requirements.txt

ENV FLASK_APP=main.py

# Working directory
WORKDIR /app

RUN pip3 install -r requirements.txt

COPY . /app

EXPOSE 5000
CMD [ "python3", "-m" , "flask", "run", "--host", "0.0.0.0" ]