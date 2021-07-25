FROM python:3.8-slim-buster

# Working directory
WORKDIR /app

# add files and install requirements
COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

ENV FLASK_APP=main.py

EXPOSE 5000
CMD [ "python3", "-m" , "flask", "run", "--host", "0.0.0.0" ]