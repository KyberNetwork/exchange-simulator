FROM python:3.6 as python-base

COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

FROM python:3.6-slim
# copy cache directory to use stored wheels
COPY --from=python-base /root/.cache /root/.cache
COPY --from=python-base /requirements.txt /requirements.txt
ADD . /exchange-simulator
VOLUME ./data:/exchange-simulator/data
WORKDIR /exchange-simulator