#Dockerfile for MEGAM
#FROM ubuntu:18.04
#
#ENV PATH="/root/miniconda3/bin:${PATH}"
#ARG PATH="/root/miniconda3/bin:${PATH}"
#
#RUN apt-get update
#RUN apt-get install -y wget ocaml make \
#    && rm -rf /var/lib/apt/lists/*
#
#RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
#    && mkdir /root/.conda \
#    && bash Miniconda3-latest-Linux-x86_64.sh -b \
#    && rm ./Miniconda3-latest-Linux-x86_64.sh
#
#COPY environment.yml .
#RUN conda env create -f environment.yml
#
#COPY . ./codi
#WORKDIR ./codi/codi/api/utils/megam_0.92
#
#RUN make clean -f Linux.mk --always-make \
#  && make depend -f Linux.mk --always-make \
#  && make Linux.mk --always-make
#
#WORKDIR /codi/codi
#SHELL ["conda", "run", "-n", "codi", "/bin/bash", "-c"]
#
#EXPOSE 8000
#ENTRYPOINT ["conda", "run", "-n", "codi", "python3", "./manage.py", "runserver", "0.0.0.0:8000"]

# Dockerfile for Sklearn
FROM continuumio/miniconda3

COPY environment.yml .
RUN conda env create -f environment.yml

COPY . ./codi
WORKDIR ./codi/codi

SHELL ["conda", "run", "-n", "codi", "/bin/bash", "-c"]

EXPOSE 8000
ENTRYPOINT ["conda", "run", "-n", "codi", "python3", "./manage.py", "runserver", "0.0.0.0:8000"]
