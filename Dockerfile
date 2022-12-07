FROM python:3.9

WORKDIR /fisco-backend

COPY . .

RUN echo $(python setup.py install)
