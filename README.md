# Project Setup and Execution Instructions

## 1. Install Anaconda

- Download and install Anaconda from the [Anaconda download page](https://www.anaconda.com/products/distribution#download-section).

## 2. Create a Virtual Environment

Open a terminal or Anaconda Prompt and run the following command to create a virtual environment:

```bash
conda create -n myenv python=3.9
```

You can replace `myenv` with your desired environment name.

## 3. Activate the Virtual Environment

Activate the virtual environment with the following command:

```bash
conda activate myenv
```

## 4. Install Required Packages

Install the necessary packages using the following command:

```bash
pip install pandas openpyxl xlsxwriter
```

## 5. Access Metabase and Download CSV File

1. Open a web browser and go to Metabase URL
2. Download the required CSV file.

## 6. Upload CSV File

Place the downloaded CSV file into the `file > upload directory`.

## 7. Run the Script

Execute the `init.py` script with the following command:

```bash
python init.py
```

## 8. Check the Results

The processed Excel file can be found in the `file > download directory`.

---

# Required CSV File List

| File Name                                |
|------------------------------------------|
| `Aws Ec2 Application Load Balancer`      |
| `Aws Ec2 Autoscaling Group`              |
| `Aws Cloudfront Distribution`            |
| `Aws Docdb Cluster`                      |
| `Aws Docdb Cluster Instance`             |
| `Aws Elasticache Cluster`                |
| `Aws Elasticache Replication Group`      |
| `Aws Ec2 Instance`                       |
| `Aws Iam Group`                          |
| `Aws Iam Role`                           |
| `Aws Iam User`                           |
| `Aws Vpc Network Acl`                    |
| `Aws Ec2 Network Load Balancer`          |
| `Aws Rds Db Cluster`                     |
| `Aws Rds Db Instance`                    |
| `Aws Vpc Route Table`                    |
| `Aws S3 Bucket`                          |
| `Aws Vpc Security Group`                 |
| `Aws Vpc Security Group Rule`            |
| `Aws Vpc Subnet`                         |
| `Aws Ec2 Target Group`                   |
| `Aws Vpc`                                |
| `Aws Vpc Internet Gateway`               |
| `Aws Ec2 Transit Gateway`                |

---
