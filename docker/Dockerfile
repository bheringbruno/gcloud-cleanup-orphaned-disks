FROM alpine:3.13.1

ENV CLOUD_SDK_VERSION=291.0.0
ENV CLOUDSDK_PYTHON=python3
ENV PATH /google-cloud-sdk/bin:$PATH
RUN addgroup gtool && \
    adduser -S -G gtool gtool

RUN mkdir /tool
RUN chown -R gtool:gtool /tool
COPY requirements.txt /tmp
COPY main.py /tool
RUN chmod 555 /tool/main.py

RUN apk update && \
    apk --no-cache upgrade && \
    apk add --no-cache python3 g++ python3-dev libffi-dev py3-pip curl --update && \
    ln -sf python3 /usr/bin/python && \
    python3 -m pip install --no-cache-dir --upgrade pip setuptools 

#Install gcloud
RUN curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-${CLOUD_SDK_VERSION}-linux-x86_64.tar.gz && \
    tar xzf google-cloud-sdk-${CLOUD_SDK_VERSION}-linux-x86_64.tar.gz && \
    rm google-cloud-sdk-${CLOUD_SDK_VERSION}-linux-x86_64.tar.gz && \
    gcloud config set core/disable_usage_reporting true && \
    gcloud config set component_manager/disable_update_check true && \
    gcloud config set metrics/environment github_docker_image && \
    gcloud --version

WORKDIR /home/gtool
ENV PATH=/home/gtool/.local/bin:$PATH

USER gtool
RUN python3 -m pip install --no-cache-dir --upgrade --user -r /tmp/requirements.txt

WORKDIR /tool

ENTRYPOINT ["/usr/bin/python3", "main.py"]
