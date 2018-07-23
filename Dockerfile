FROM python:3.6
RUN apt-get update
RUN apt-get install -y python-dev python-pip nginx
COPY Pipfile Pipfile.lock /
RUN pip install pipenv==2018.7.1 && \
    pipenv lock --requirements > requirements.txt && \
    pip install -r requirements.txt
COPY ./nginx.conf /etc/nginx/
COPY ./nginx_conf/* /etc/nginx/conf.d/
ADD . /exchange-simulator
VOLUME ./data:/exchange-simulator/data
WORKDIR /exchange-simulator