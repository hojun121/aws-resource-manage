import pandas as pd
import json


def extract_security_group_ids(vpc_security_groups):
    """Extract and return security group IDs from VPC security group data."""
    if pd.isna(vpc_security_groups) or not vpc_security_groups.strip():
        return ''

    try:
        security_groups = json.loads(vpc_security_groups.replace("'", "\""))
        return ', '.join(sg.get('VpcSecurityGroupId', '') for sg in security_groups)
    except json.JSONDecodeError as e:
        print(f"JSON decoding error in security group IDs: {e}")
        return ''
    except Exception as e:
        print(f"Unexpected error in security group extraction: {e}")
        return ''


def extract_subnet_ids(subnets):
    """Extract and return subnet IDs from subnet data."""
    if pd.isna(subnets) or not subnets.strip():
        return ''

    try:
        subnet_data = json.loads(subnets.replace("'", "\""))
        return ', '.join(subnet.get('SubnetIdentifier', '') for subnet in subnet_data)
    except json.JSONDecodeError as e:
        print(f"JSON decoding error in subnet IDs: {e}")
        return ''
    except Exception as e:
        print(f"Unexpected error in subnet extraction: {e}")
        return ''


def format_backup_retention_period(period):
    """Format the backup retention period."""
    if pd.notna(period) and period > 0:
        days_label = 'day' if period == 1 else 'days'
        return f'Enabled ({int(period)} {days_label})'
    return 'Disabled'


def merge_rds_instance_and_cluster_data(instance_data, cluster_data):
    """Perform a left join on instance and cluster data."""
    return instance_data.merge(
        cluster_data,
        on='Db Cluster Identifier',
        how='left',
        suffixes=('_instance', '_cluster')
    )


def transform_rds_data(instance_data, cluster_data):
    """Transform merged RDS instance and cluster data into the desired format."""
    merged_data = merge_rds_instance_and_cluster_data(instance_data, cluster_data)

    transformed_data = pd.DataFrame({
        'Cluster Name': merged_data['Db Cluster Identifier'],
        'DB Name': merged_data['Db Instance Identifier'],
        'Port': merged_data['Endpoint Port'].fillna('-'),
        'Engine Version': merged_data['Engine Version_instance'].fillna('-'),
        'Size': merged_data['Class'].fillna('-'),
        'Subnet Group ID': merged_data['Db Subnet Group Name'].fillna('-'),
        'Subnet ID': merged_data['Subnets'].apply(extract_subnet_ids).fillna('-'),
        'Parameter Group': merged_data['Db Cluster Parameter Group'].fillna('-'),
        'Security Group': merged_data['Vpc Security Groups_instance'].apply(extract_security_group_ids).fillna('-'),
        # 'Cluster Endpoint': merged_data['Endpoint'].fillna('-'),
        # 'Reader Endpoint': merged_data['Reader Endpoint'].fillna('-'),
        'Endpoint': merged_data['Endpoint Address'].fillna('-'),
        'Backup': merged_data['Backup Retention Period_instance'].apply(format_backup_retention_period).fillna(
            'Disabled'),
        'Encryption At Rest': merged_data['Storage Encrypted_instance'].apply(lambda x: 'Yes' if x else 'No').fillna(
            'No'),
        'Description': merged_data['Db Subnet Group Description'].fillna('-'),
        'Tier': merged_data['Promotion Tier'].fillna('-'),
        'Compared with Last Month': '-'
    })

    return transformed_data


def load_and_transform_rds_data(rds_cluster_csv_file, rds_instance_csv_file):
    """Load, transform, and return RDS instance and cluster data."""
    # Load the CSV files
    instance_data = pd.read_csv(rds_instance_csv_file, encoding='utf-8')
    cluster_data = pd.read_csv(rds_cluster_csv_file, encoding='utf-8')

    # Transform the data and return the result
    return transform_rds_data(instance_data, cluster_data)
