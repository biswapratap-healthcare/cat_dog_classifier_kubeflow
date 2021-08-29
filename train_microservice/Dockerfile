FROM python:3.8-slim-buster
RUN apt-get update
RUN mkdir /train_microservice
COPY main.py /train_microservice
COPY train.py /train_microservice
COPY requirements.txt /train_microservice
WORKDIR train_microservice
RUN pip install -r requirements.txt
ENTRYPOINT ["python", "main.py"]
