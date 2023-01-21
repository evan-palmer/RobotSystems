FROM python:3 as base

ENV DEBIAN_FRONTEND=noninteractive

# Update pip to latest version
RUN pip3 install --upgrade pip

# Install all required Python packages
RUN pip3 install \
    pandas \
    numpy \
    opencv-python \
    PyYAML


FROM base as development

# Install dev apt packages
RUN apt-get update \
    && apt-get -y install --no-install-recommends \
    apt-utils \
    python3-dev \
    python3-pip \
    git \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

# Install debugging/linting Python packages
RUN pip3 install \
    pipenv \
    black \
    flake8 \
    isort \
    pydocstyle \
    mypy \
    bandit \
    coverage \
    pre-commit \
    tox \
    rstcheck

# Install picar dependencies
RUN git clone https://github.com/sunfounder/robot-hat.git \
    && python3 -m pip install ./robot-hat

# Configure a new non-root user
ARG USERNAME=developer
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && apt-get update \
    && apt-get install -y sudo \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME \
    && rm -rf /var/lib/apt/lists/* \
    && echo "source /usr/share/bash-completion/completions/git" >> /home/$USERNAME/.bashrc

# Add the .local/bin directory to the path
ENV PATH "${PATH}:/home/$USERNAME/.local/bin"
