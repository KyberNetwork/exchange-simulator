FROM python:3.6
COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt
ADD . /exchange-simulator
VOLUME ./data:/exchange-simulator/data
WORKDIR /exchange-simulator

# EXPOSE 5100
# EXPOSE 5200
# EXPOSE 5300

#FROM tiangolo/uwsgi-nginx:python3.6
#FROM nginx
#RUN apt-get update -y 
#RUN apt-get install -y python-pip python-dev nginx libssl-dev
#COPY deployment/* /etc/nginx/sites-enabled/
#COPY requirements.txt /tmp/
#RUN pip install -r /tmp/requirements.txt
#ADD . /exchange-simulator
#WORKDIR /exchange-simulator
#EXPOSE 5100
#ENTRYPOINT uwsgi --emperor /exchange-simulator/vassals

# FROM tiangolo/uwsgi-nginx:python3.6
# COPY requirements.txt /tmp/
# RUN pip install -r /tmp/requirements.txt
# ADD . /exchange-simulator
# ENV UWSGI_INI /exchange-simulator/uwsgi.ini
# EXPOSE 5100