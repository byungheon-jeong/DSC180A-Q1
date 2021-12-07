FROM ucsdets/datahub-base-notebook:2021.2-stable

USER root
ARG DEBIAN_FRONTEND=noninteractive
RUN mkdir -p /projectHome
RUN useradd -m bam -s /projectHome
RUN chown bam /projectHome

RUN apt-get update --fix-missing &&\
        apt-get -y install \
        # git \
        nano \
        python3-pip

RUN pip3 install jupyterlab\
        scikit-learn

COPY ./truEnv.yml /projectHome/requirements.yml
RUN conda env create -f /projectHome/requirements.yml
# RUN git clone https://github.com/byungheon-jeong/dsc180a-assign5.git /home/projectHome/

RUN echo "source activate capstone" > ~/.bashrc
# RUN pip install "napari[all]"

WORKDIR /home/projectHome/

CMD ["/bin/bash"]


