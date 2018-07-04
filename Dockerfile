FROM python:3.6
RUN apt-get update
RUN apt-get install -y python-dev python-pip nginx
COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt
COPY ./nginx.conf /etc/nginx/
COPY ./nginx_conf/* /etc/nginx/conf.d/
ADD . /exchange-simulator
VOLUME ./data:/exchange-simulator/data
WORKDIR /exchange-simulator