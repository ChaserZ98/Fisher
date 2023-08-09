FROM python:3.11.4-alpine
LABEL maintainer="Feiyu Zheng <feiyuzheng98@gmail.com>"
VOLUME /usr/share/Fisher
COPY requirements.txt /usr/share/Fisher/requirements.txt
WORKDIR /usr/share/Fisher
RUN pip install -r requirements.txt
