FROM ubuntu:22.04

# Setup prerequisites (as root)
# Install AWS CLI
# Add Steampipe repository and install Steampipe
USER root
RUN apt-get update -y \
 && apt-get install -y git curl unzip sudo gnupg2 software-properties-common openjdk-11-jre-headless vim wget \
 && curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
 && unzip awscliv2.zip \
 && ./aws/install \
 && rm -rf awscliv2.zip aws/ \
 && curl -fsSL https://github.com/turbot/steampipe/releases/latest/download/steampipe_linux_amd64.deb -o steampipe.deb \
 && apt-get install -y ./steampipe.deb \
 && rm steampipe.deb \
 && useradd -m steampipe \
 && echo "steampipe ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Intall Steampipe
USER steampipe
SHELL ["/bin/bash", "-c"]
# Install Anaconda 24.5
RUN git clone -b aws-inventory-automation-db-conn https://github.com/hojun121/aws-resource-manage.git $HOME/hanwha-inventory \
    && steampipe plugin install steampipe aws \
    && sudo wget https://repo.anaconda.com/archive/Anaconda3-2024.06-1-Linux-x86_64.sh -O anaconda.sh \
    && sh anaconda.sh -b -p $HOME/anaconda \
    && eval "$($HOME/anaconda/bin/conda shell.bash hook)" \
    && $HOME/anaconda/bin/conda init \
    && sudo apt update && sudo apt install -y build-essential libpq-dev \
    && pip install pandas openpyxl xlsxwriter SQLAlchemy psycopg2 tqdm

WORKDIR /home/steampipe/hanwha-inventory
