import pandas as pd

# Subnet 및 Security Group을 처리하는 함수들
def extract_subnets(subnet_ids):
    return ', '.join(subnet_ids) if isinstance(subnet_ids, list) else 'None'

def extract_security_groups(security_groups):
    return ', '.join([sg['GroupName'] for sg in security_groups]) if isinstance(security_groups, list) else 'None'

def extract_route_tables(value):
    return ', '.join(value) if isinstance(value, list) and value else 'None'

# Terraform 여부를 확인하는 함수
def extract_terraform(tags):
    if isinstance(tags, list):
        for tag in tags:
            if tag.get('Key') == 'Terraform' and tag.get('Value') == 'True':
                return 'Yes'
    return 'No'

# VPC 엔드포인트 데이터 변환 함수
def transform_vep_data(vep_data):
    # 필수 컬럼 변환 및 추가 작업
    vep_data['subnets'] = vep_data['subnet_ids'].apply(extract_subnets)
    vep_data['security_groups'] = vep_data['groups'].apply(extract_security_groups)
    vep_data['terraform'] = vep_data['tags'].apply(extract_terraform)

    # 최종 변환된 데이터 생성
    transformed_data = pd.DataFrame({
        'Name': vep_data['title'],
        'ID': vep_data['vpc_endpoint_id'],
        'VPC ID': vep_data['vpc_id'],
        'Service Name': vep_data['service_name'],
        'Type': vep_data['vpc_endpoint_type'],
        'Route Table': vep_data['route_table_ids'].apply(extract_route_tables),
        'Subnet (Interface)': vep_data['subnets'],
        'Security Group (Interface)': vep_data['security_groups'],
        'Terraform': vep_data['terraform']
    })

    # Sort VPC Endpoint by VPC Endpoint Name in Ascending order
    transformed_data = transformed_data.sort_values(by='Name', ascending=False)

    return transformed_data

def load_and_transform_vep_data(vep_data):
    return transform_vep_data(vep_data)
