# syntax=docker/dockerfile:1.2
###############################################################################

# Base Image
ARG BASE_IMAGE=python:3.7-slim
FROM ${BASE_IMAGE} AS build-stage

# Labels
LABEL version="1.0"
LABEL maintainer="lollococce"

# Envs
ENV HOME /usr/local/pdfer

# Install main packages
RUN set -ex \
    && buildDeps=' \
        python3-dev \
        libkrb5-dev \
        libsasl2-dev \
        libssl-dev \
        libffi-dev \
        build-essential \
        libblas-dev \
        liblapack-dev \
        libpq-dev \
        git \
    ' \
    && apt-get update -yqq \
    && apt-get upgrade -yqq \
    && apt-get install -yqq --no-install-recommends \
        ${buildDeps} \
        sudo \
        python3-pip \
        python3-requests \
        default-mysql-client \
        default-libmysqlclient-dev \
        apt-utils \
        curl \
        rsync \
        netcat \
        locales \
        gcc \
        poppler-utils \
        ffmpeg \
        libsm6 \
        libxext6 \
        libgl1-mesa-glx \
        tesseract-ocr \
    && apt-get purge --auto-remove -yqq ${buildDeps} \
    && apt-get autoremove -yqq --purge \
    && apt-get clean \
    && rm -rf \
        /var/lib/apt/lists/* \
        /tmp/* \
        /var/tmp/* \
        /usr/share/man \
        /usr/share/doc \
        /usr/share/doc-base

###############################################################################
#
# Next, build the actual image that will run in production.

# Copy entrypoint.sh
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Be sure to Install crucial packages for psycopg2
RUN sudo apt-get update && sudo apt-get -y install libpq-dev

###############################################################################
# # # # # # # # # # # # # # # # # END OF ROOT # # # # # # # # # # # # # # # # #

# Create a new user to run as
RUN chown -R pdfer: ${HOME}
USER pdfer

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH ${HOME}

ENV PYTHONFAULTHANDLER=1

# Set Working Dir
WORKDIR ${HOME}

ENTRYPOINT ["/entrypoint.sh"]
###############################################################################
