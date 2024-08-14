FROM ubuntu:22.04

# Setup prerequisites (as root)
USER root
RUN apt-get update -y \
 && apt-get install -y git curl unzip sudo gnupg2 software-properties-common openjdk-11-jre-headless vim

# Install AWS CLI
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
 && unzip awscliv2.zip \
 && ./aws/install \
 && rm -rf awscliv2.zip aws/

# Add Steampipe repository and install Steampipe
RUN curl -fsSL https://github.com/turbot/steampipe/releases/latest/download/steampipe_linux_amd64.deb -o steampipe.deb \
 && apt-get install -y ./steampipe.deb \
 && rm steampipe.deb

# Create the steampipe user and group
RUN useradd -m steampipe

# Grant sudo privileges to steampipe user
RUN echo "steampipe ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Install Steampipe plugins as steampipe user
USER steampipe
RUN steampipe plugin install steampipe aws && sudo apt-get install vim -y

# Return to root to set up entrypoint and run Metabase
USER root

# Install Metabase
RUN curl -LO https://downloads.metabase.com/v0.45.2/metabase.jar && \
    mkdir -p /opt/metabase && \
    mv metabase.jar /opt/metabase/ && \
    git clone --depth 1 https://github.com/turbot/steampipe-mod-aws-insights.git && \
    mv steampipe-mod-aws-insights /home/steampipe

# Expose necessary ports
EXPOSE 3000 9194

# Start Metabase and make Steampipe available
CMD ["sh", "-c", "java -jar /opt/metabase/metabase.jar"]

