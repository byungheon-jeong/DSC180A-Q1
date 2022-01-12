FROM ucsdets/datahub-base-notebook:2021.1-stable

USER root
ARG DEBIAN_FRONTEND=noninteractive
RUN mkdir -p /projectHome
RUN useradd -m bam -s /projectHome -s /bin/bash 
RUN chown bam -R /projectHome /home/jovyan/ /bin/bash 

RUN apt-get update --fix-missing &&\
        apt-get -y install \
        git \
        nano \
        python3-pip

RUN pip3 install jupyterlab\
        scikit-learn

COPY ./truEnv.yml /projectHome/requirements.yml
RUN conda env create -f /projectHome/requirements.yml
# RUN git clone https://github.com/byungheon-jeong/dsc180a-assign5.git /home/projectHome/

RUN pip install "napari[all]"

USER bam
WORKDIR /home/projectHome/

RUN echo "source activate capstone" > ~/.bashrc
ENV PATH /opt/conda/envs/capstone/bin:$PATH


