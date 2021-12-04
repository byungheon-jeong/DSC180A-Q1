FROM madmanfred/qt5-builder

USER root

RUN apt-get update --fix-missing
RUN apt-get -y install \
        git \
        python3-pip \
        numpy

RUN pip3 install "napari[all]"\
        scikit-learn