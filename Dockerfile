FROM python:3.6 as python-base
RUN apt-get update && \
	apt-get install -y python-dev python-pip nginx && \
	rm -rf /var/lib/apt/lists/*

COPY Pipfile Pipfile.lock /

RUN pip install pipenv==2018.7.1 && \
    pipenv lock --requirements > requirements.txt && \
	pip install -r requirements.txt

FROM python:3.6-slim
# copy cache directory to use stored wheels
COPY --from=python-base /root/.cache /root/.cache
COPY --from=python-base /requirements.txt /requirements.txt

RUN apt-get update && \
	apt-get install -y libxml2 && \
	rm -rf /var/lib/apt/lists/*

COPY ./nginx.conf /etc/nginx/
COPY ./nginx_conf/* /etc/nginx/conf.d/
ADD . /exchange-simulator
RUN pip install -r /requirements.txt && \
	rm -rf /root/.cache /requirements.txt

VOLUME ./data:/exchange-simulator/data
WORKDIR /exchange-simulator
