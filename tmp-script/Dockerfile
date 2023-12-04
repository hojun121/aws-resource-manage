FROM ubuntu:22.04

# Update the package list, install sudo, create a non-root user, and grant password-less sudo permissions
RUN apt update && \
    apt install -y sudo curl git && \
    addgroup --gid 1000 nonroot && \
    adduser --uid 1000 --gid 1000 --disabled-password --gecos "" nonroot && \
    echo 'nonroot ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers

# Set the non-root user as the default user
USER nonroot

WORKDIR /home/nonroot/app

RUN sudo chmod -R 755 /home/nonroot/app && \
    sudo /bin/sh -c "$(curl -fsSL https://raw.githubusercontent.com/turbot/steampipe/main/install.sh)" && \
    steampipe plugin install steampipe && \
    steampipe plugin install aws && \
    sudo git clone https://github.com/turbot/steampipe-mod-aws-insights.git

WORKDIR /home/nonroot/app/steampipe-mod-aws-insights
ENTRYPOINT ["steampipe", "service", "start", "--foreground"]
CMD ["--dashboard", "--dashboard-listen", "network"]
EXPOSE 9194
EXPOSE 9193
