# Make sure you have installed the NVIDIA driver >= 361.93 and Docker >= 19.03
# https://github.com/NVIDIA/nvidia-docker/wiki/Installation-(Native-GPU-Support)#prerequisites
ARG CUDA_VERSION=11.1
ARG CUDNN_VERSION=8
ARG UBUNTU_VERSION=18.04

FROM nvidia/cuda:${CUDA_VERSION}-cudnn${CUDNN_VERSION}-devel-ubuntu${UBUNTU_VERSION}
LABEL maintainer="Happify AI Team (Thomas Yue, thomas@happify.com)"
LABEL description="Efficient Research template based on Pytorch Lightning, Hydra & HuggingFace"

ENV ENV_NAME=myenv

# Copy all files
# Create a working directory
RUN mkdir /workspace
ADD . /workspace/project
WORKDIR /workspace/project

# Install some basic utilities
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    tmux \
    vim \
    && rm -rf /var/lib/apt/lists/*

# Switch to bash shell
SHELL ["/bin/bash", "-c"]

# Install Miniconda and Python
ADD https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh miniconda3.sh
RUN /bin/bash miniconda3.sh -b -p /conda \
    && rm miniconda3.sh \
    && echo export PATH=/conda/bin:$PATH >> .bashrc
ENV PATH="/conda/bin:${PATH}"

# Update conda
RUN conda update -n base -c defaults conda

# Create conda virtual environment
RUN conda env create -f conda_env_gpu.yaml -n myenv
RUN conda init bash

# Set myenv to default virtual environment
RUN echo "source activate ${ENV_NAME}" >> ~/.bashrc
