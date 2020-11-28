FROM ubuntu:18.04

## Install General Requirements
RUN apt-get update && \
        apt-get install -y --no-install-recommends \
        apt-utils \
        build-essential \
        cmake \
        git \
        wget \
        nano \
        python3-pip \
        software-properties-common

RUN apt-get install -y python3.7
RUN python3.7 -m pip install pip
RUN pip3 install --upgrade pip
RUN python3.7 -m pip install numpy pandas requests
RUN pip3 install numpy pandas requests
		
WORKDIR /work

# copy entire directory where docker file is into docker container at /work
COPY . /work/

RUN chmod 777 train.sh
RUN chmod 777 test.sh
