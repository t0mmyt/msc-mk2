FROM ubuntu:16.04
MAINTAINER Tom Taylor <tom+dockerfiles@tomm.yt>

# Python installation moved to before ARGs to utilise build cache
# and add app user
RUN apt-get -qq update &&\
    DEBIAN_FRONTEND=noninteractive apt-get -yqq install \
      python3 python3-pip && \
      pip3 install --upgrade pip && \
    groupadd app && useradd -r -g app app

# Service name and port to expose
ARG SERVICE
ARG PORT

# Install dependencies (xargs hack to force order)
COPY services/${SERVICE}/requirements.txt /
RUN xargs -L 1 pip install < /requirements.txt

# Install service
COPY services/${SERVICE} /opt/${SERVICE}
WORKDIR /opt/${SERVICE}

EXPOSE ${PORT}
USER app
ENTRYPOINT ["./run.sh"]
