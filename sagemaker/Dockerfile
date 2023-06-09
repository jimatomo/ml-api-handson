FROM ubuntu:20.04

# Set a docker label to advertise multi-model support on the container
LABEL com.amazonaws.sagemaker.capabilities.multi-models=true
# Set a docker label to enable container to use SAGEMAKER_BIND_TO_PORT environment variable if present
LABEL com.amazonaws.sagemaker.capabilities.accept-bind-to-port=true


# Upgrade installed packages
RUN apt-get update && apt-get upgrade -y && apt-get clean

# Python package management and basic dependencies
RUN apt-get install -y curl python3.9 python3.9-dev python3.9-distutils

# Register the version in alternatives
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.9 1

# Set python 3 as the default python
RUN update-alternatives --set python /usr/bin/python3.9

# Install necessary dependencies for MMS and SageMaker Inference Toolkit
RUN apt-get -y install --no-install-recommends \
    build-essential \
    ca-certificates \
    openjdk-8-jdk-headless \
    curl \
    vim \
    && rm -rf /var/lib/apt/lists/* \
    && python --version \
    && curl -O https://bootstrap.pypa.io/get-pip.py \
    && python get-pip.py

RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 1
RUN update-alternatives --install /usr/local/bin/pip pip /usr/local/bin/pip3 1

# Install MXNet, MMS, and SageMaker Inference Toolkit to set up MMS
RUN pip3 --no-cache-dir install mxnet \
                                multi-model-server \
                                sagemaker-inference \
                                retrying

# Install lightgbm and pandas
RUN pip3 --no-cache-dir install numpy \
                                pandas \
                                lightgbm

# Copy code to the image
COPY ml/ /opt/ml
RUN chmod +x /opt/ml/code/*.py
ENV PYTHONPATH=/opt/ml/code

# Define an entrypoint script for the docker image
ENTRYPOINT ["python", "/opt/ml/code/entrypoint.py"]

# Define command to be passed to the entrypoint
CMD ["serve"]