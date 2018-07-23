FROM python:3.6
RUN pip install pipenv
RUN apt-get update
RUN apt-get install -y python-dev python-pip nginx
COPY Pipfile .
COPY Pipfile.lock .
RUN pipenv install
COPY ./nginx.conf /etc/nginx/
COPY ./nginx_conf/* /etc/nginx/conf.d/
ADD . /exchange-simulator
VOLUME ./data:/exchange-simulator/data
WORKDIR /exchange-simulator