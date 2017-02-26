FROM ubuntu:16.04
MAINTAINER Tom Taylor <tom+dockerfiles@tomm.yt>

# Python installation moved to before ARGs to utilise build cache
RUN apt-get -qq update &&\
    DEBIAN_FRONTEND=noninteractive apt-get -yqq install \
      nginx python3 python3-pip python3-numpy python3-scipy && \
      pip3 install --upgrade pip

# Service name and port to expose
ARG SERVICE
ARG PORT

# Install dependencies
COPY services/${SERVICE}/requirements.txt /
RUN pip3 install -r /requirements.txt

# Install service
COPY services/${SERVICE} /opt/${SERVICE}
WORKDIR /opt/${SERVICE}

EXPOSE ${PORT}
ENTRYPOINT ["./run.sh"]
