FROM ubuntu:22.04

ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY
ARG AWS_REGION

# Update the package list, install sudo, create a non-root user, and grant password-less sudo permissions
RUN apt update && \
    apt install -y sudo curl git unzip && \
    addgroup --gid 1000 nonroot && \
    adduser --uid 1000 --gid 1000 --disabled-password --gecos "" nonroot && \
    echo 'nonroot ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers

# Set the non-root user as the default user
USER nonroot

WORKDIR /home/nonroot/app

RUN sudo chmod -R 755 /home/nonroot/app && \
    sudo curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    sudo unzip awscliv2.zip && sudo rm -f awscliv2.zip && \
    sudo ./aws/install && \
    sudo /bin/sh -c "$(curl -fsSL https://raw.githubusercontent.com/turbot/steampipe/main/install.sh)" && \
    steampipe plugin install steampipe && \
    steampipe plugin install aws && \
    sudo git clone https://github.com/turbot/steampipe-mod-aws-insights.git && \
    aws configure set aws_access_key_id $AWS_ACCESS_KEY_ID && \
    aws configure set aws_secret_access_key $AWS_SECRET_ACCESS_KEY && \
    aws configure set region $AWS_REGION && \ 
    aws configure set output "json" && \
    aws iam generate-credential-report

WORKDIR /home/nonroot/app/steampipe-mod-aws-insights
ENTRYPOINT ["steampipe", "service", "start", "--foreground"]
CMD ["--dashboard", "--dashboard-listen", "network"]
EXPOSE 9194
EXPOSE 9193
