FROM ubuntu:20.04

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get install -y python3 \
 python3-pip \
 python3-dev \
 python3-setuptools \
 nginx \
 uwsgi-core \
 libpcre3 \
 libpcre3-dev 

RUN mkdir dubois
COPY requirements.txt /dubois
WORKDIR /dubois

RUN pip3 install -r requirements.txt

COPY . .
RUN chmod +x boot.sh; chmod -R 777 /dubois/app/static;

ENV DUBOIS_ENTRYPOINT "/dubois"
ENV DUBOIS_TITLE "Experiment"
ENV DUBOIS_ABSTRACT "<p>Abstract goes here</p>"

ENTRYPOINT ./boot.sh