FROM python:3.6
COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt
ADD . /exchange-simulator
VOLUME ./data:/exchange-simulator/data
WORKDIR /exchange-simulator