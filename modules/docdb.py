import pandas as pd
import json


def extract_security_group_ids(vpc_security_groups):
    """보안 그룹 ID를 추출합니다."""
    try:
        if pd.isna(vpc_security_groups) or not vpc_security_groups.strip():
            return ''

        # JSON 문자열을 파싱하여 보안 그룹 정보 추출
        security_groups = json.loads(vpc_security_groups.replace("'", "\""))

        # 'VpcSecurityGroupId' 값을 쉼표로 구분된 문자열로 반환
        return ', '.join(sg.get('VpcSecurityGroupId', '') for sg in security_groups)
    except json.JSONDecodeError as e:
        print(f"JSON 디코딩 오류 발생: {e}")
        return ''
    except Exception as e:
        print(f"기타 오류 발생: {e}")
        return ''


def extract_subnet_ids(subnets):
    """서브넷 ID를 추출합니다."""
    try:
        if pd.isna(subnets) or not subnets.strip():
            return ''

        subnet_data = json.loads(subnets.replace("'", "\""))
        return ', '.join(subnet.get('SubnetIdentifier', '') for subnet in subnet_data)
    except json.JSONDecodeError as e:
        print(f"JSON 디코딩 오류 발생: {e}")
        return ''
    except Exception as e:
        print(f"기타 오류 발생: {e}")
        return ''


def format_backup_retention_period(period):
    """백업 보존 기간을 형식화합니다."""
    try:
        if pd.notna(period) and period > 0:
            days_label = 'day' if period == 1 else 'days'
            return f'Enabled ({int(period)} {days_label})'
        return 'Disabled'
    except Exception as e:
        print(f"백업 보존 기간 처리 중 오류 발생: {e}")
        return 'Disabled'


def transform_docdb_data(docdb_cluster_csv_file, docdb_instance_csv_file):
    """DocDB 클러스터와 인스턴스 데이터를 변환합니다."""
    # 클러스터와 인스턴스 데이터를 로드합니다.
    cluster_data = pd.read_csv(docdb_cluster_csv_file, encoding='utf-8')
    instance_data = pd.read_csv(docdb_instance_csv_file, encoding='utf-8')

    # 인스턴스 데이터를 기준으로 병합합니다.
    merged_data = instance_data.merge(
        cluster_data,
        left_on='Db Cluster Identifier',
        right_on='Db Cluster Identifier',
        how='left',
        suffixes=('_instance', '_cluster')
    )

    # DataFrame 생성
    transformed_data = pd.DataFrame({
        'Cluster / DB Name': merged_data['Db Instance Identifier'],
        'Port': merged_data['Endpoint Port'],
        'Engine Version': merged_data['Engine Version_instance'],
        'Size': merged_data['Db Instance Class'],
        'Subnet Group ID': merged_data['Db Subnet Group Name'],
        'Subnet ID': merged_data['Subnets'].apply(extract_subnet_ids),
        'Parameter Group': merged_data['Db Cluster Parameter Group'],
        'Security Group': merged_data['Vpc Security Groups_instance'].apply(extract_security_group_ids),
        'Cluster Endpoint': merged_data['Endpoint'],
        'Reader Endpoint': merged_data['Reader Endpoint'],
        'Backup': merged_data['Backup Retention Period_instance'].apply(format_backup_retention_period),
        'Encryption At Rest': merged_data['Storage Encrypted_instance'].apply(lambda x: 'Yes' if x else 'No'),
        'Description': merged_data['Db Subnet Group Description'],
        # 'CloudWatch': merged_data['Enabled Cloudwatch Logs Exports_instance'].apply(
        #     lambda x: ', '.join(json.loads(x.replace("'", "\""))) if pd.notna(x) else 'None'),
        'Tier': merged_data['Promotion Tier'],
        'Compared with Last Month': '-'
    })

    return transformed_data


def load_and_transform_docdb_data(docdb_docdb_cluster_csv_file, docdb_docdb_instance_csv_file):
    return transform_docdb_data(docdb_docdb_cluster_csv_file, docdb_docdb_instance_csv_file)
