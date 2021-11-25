FROM huanjason/scikit-learn:latest

USER root
ARG DEBIAN_FRONTEND=noninteractive
RUN mkdir -p /projectHome
RUN useradd -m bam -s /projectHome
RUN chown bam /projectHome

RUN apt-get update --fix-missing &&\
        apt-get -y install \
        git \
        nano

RUN git clone https://github.com/byungheon-jeong/DSC180A-Q1.git /home/projectHome/


USER bam
WORKDIR /home/projectHome/