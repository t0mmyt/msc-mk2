FROM ubuntu:16.04
MAINTAINER Tom Taylor <tom+dockerfiles@tomm.yt>

EXPOSE 8000

RUN apt-get -qq update &&\
    DEBIAN_FRONTEND=noninteractive apt-get -yqq install \
      python3 python3-pip &&\
    pip3 install flup6 flask flask_restful requests gevent

COPY tsdatastore /tsdatastore
COPY run.py setup.py /
RUN python3 setup.py install

ENTRYPOINT ["/run.py"]
