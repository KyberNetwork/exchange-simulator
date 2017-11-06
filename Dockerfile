FROM python:3.6
COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt
ADD . /exchange-simulator
WORKDIR /exchange-simulator