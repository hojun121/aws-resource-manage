FROM ubuntu:22.04

# Setup prerequisites (as root)
# Install AWS CLI
# Add Steampipe repository and install Steampipe
USER root
RUN apt-get update -y \
 && apt-get install -y git curl sudo unzip vim wget build-essential libpq-dev \
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
    && sudo apt update && sudo apt-get install python3 python3-pip -y \
    && pip install pandas openpyxl xlsxwriter SQLAlchemy psycopg2 tqdm \
    && sudo ln -s /usr/bin/python3 /usr/bin/python

WORKDIR /home/steampipe/hanwha-inventory
