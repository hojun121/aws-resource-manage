# AWS Resource Inventory Extractor 

A module that uses awscli and the open-source tool Steampipe to extract AWS resources and export them to a structured inventory file.

You can verify the explaination on [Detail Documantation(Jira Confluence)](https://hanwhavision.atlassian.net/wiki/x/T4KKK).

## Steps of Operation
- [1/4] Authenticate with AWS using awscli: IAM or SSO.
- [2/4] Setup Steampipe config file.
- [3/4] Extract AWS resources into an in-memory PostgreSQL.
- [4/4] Extract an in-memory PostgreSQL to structured inventory file.

## Pre-requirements
- For fater extraction, 2 vCpu & 8 Ram are recommended
- Docker version: v24.0.5
- AWS Account
- Steampipe Config

## Execution Guide
### Dockerfile Build
```bash
docker build -t {{imageName}} .
```
### Container Run
```bash
docker run --rm -it -v {{Your Host Directory}}:/app/inventory {{imageName}} sh extract_inventory.sh
```

The extracted inventory will be created in {{Your Host Directory}}.
