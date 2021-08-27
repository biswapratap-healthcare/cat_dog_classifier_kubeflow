FROM python:3.8-slim-buster
RUN mkdir /feature_microservice
COPY main.py /feature_microservice
COPY rest_client.py /feature_microservice
COPY requirements.txt /feature_microservice
WORKDIR feature_microservice
RUN pip install -r requirements.txt
ENTRYPOINT ["python", "main.py"]
