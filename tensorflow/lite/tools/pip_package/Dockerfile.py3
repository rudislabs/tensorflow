# Copyright 2022 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

ARG IMAGE
FROM ubuntu:24.04 
RUN touch /var/mail/ubuntu && chown ubuntu /var/mail/ubuntu && userdel -r ubuntu
ARG PYTHON_VERSION
ARG NUMPY_VERSION

COPY update_sources.sh /
RUN /update_sources.sh

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC \
    apt-get install -y \
      build-essential \
      software-properties-common \
      zlib1g-dev  \
      curl \
      wget \
      unzip \
      git && \
    apt-get clean

# Install Bazel.
RUN wget https://github.com/bazelbuild/bazelisk/releases/download/v1.15.0/bazelisk-linux-amd64 \
  -O /usr/local/bin/bazel && chmod +x /usr/local/bin/bazel

RUN echo '\
Types: deb\n\
Architectures: amd64\n\
URIs: http://us.archive.ubuntu.com/ubuntu/\n\
Suites: noble noble-updates noble-backports\n\
Components: main restricted universe multiverse\n\
Signed-By: /usr/share/keyrings/ubuntu-archive-keyring.gpg\n\n\
Types: deb\n\
Architectures: amd64\n\
URIs: http://security.ubuntu.com/ubuntu/\n\
Suites: noble-security\n\
Components: main restricted universe multiverse\n\
Signed-By: /usr/share/keyrings/ubuntu-archive-keyring.gpg\n\n\
Types: deb\n\
Architectures: arm64 armhf\n\
URIs: http://ports.ubuntu.com/ubuntu-ports\n\
Suites: noble noble-updates noble-backports noble-security\n\
Components: main restricted universe multiverse\n\
Signed-By: /usr/share/keyrings/ubuntu-archive-keyring.gpg\
' > /etc/apt/sources.list.d/ubuntu.sources

# Install Python packages.
RUN dpkg --add-architecture armhf
RUN dpkg --add-architecture arm64
RUN yes | add-apt-repository ppa:deadsnakes/ppa
RUN apt-get update && \
    apt-get install -y \
      python$PYTHON_VERSION \
      python$PYTHON_VERSION-dev \
      python$PYTHON_VERSION-venv \
      python3-setuptools \
      libpython$PYTHON_VERSION-dev \
      libpython$PYTHON_VERSION-dev:armhf \
      libpython$PYTHON_VERSION-dev:arm64
RUN ln -sf /usr/bin/python$PYTHON_VERSION /usr/bin/python3
RUN curl -OL https://bootstrap.pypa.io/get-pip.py
RUN python3 get-pip.py --break-system-packages
RUN rm get-pip.py
RUN pip3 install --upgrade pip --break-system-packages
RUN pip3 install wheel --break-system-packages
RUN pip3 install numpy~=$NUMPY_VERSION setuptools pybind11 --break-system-packages
RUN ln -sf /usr/include/python$PYTHON_VERSION /usr/include/python3
RUN ln -sf /usr/local/lib/python$PYTHON_VERSION/dist-packages/numpy/core/include/numpy /usr/include/python3/numpy
RUN curl -OL https://github.com/Kitware/CMake/releases/download/v3.16.8/cmake-3.16.8-Linux-x86_64.sh
RUN mkdir /opt/cmake
RUN sh cmake-3.16.8-Linux-x86_64.sh --prefix=/opt/cmake --skip-license
RUN ln -s /opt/cmake/bin/cmake /usr/local/bin/cmake

ENV CI_BUILD_PYTHON=python$PYTHON_VERSION
ENV CROSSTOOL_PYTHON_INCLUDE_PATH=/usr/include/python$PYTHON_VERSION

COPY with_the_same_user /
