import pandas as pd
import json


def transform_subnet_data(subnet_csv_file, rt_csv_file, network_acl_csv_file):
    # CSV 파일을 DataFrame으로 읽기
    subnet_df = pd.read_csv(subnet_csv_file, encoding='utf-8')
    rt_df = pd.read_csv(rt_csv_file, encoding='utf-8')
    network_acl_df = pd.read_csv(network_acl_csv_file, encoding='utf-8')

    # Route Table 정보를 딕셔너리 형태로 변환
    def parse_associations(json_str):
        try:
            associations = json.loads(json_str)
            return {assoc.get('SubnetId', ''): {'Route Table ID': assoc.get('RouteTableId', ''), 'Title': assoc.get('RouteTableAssociationId', '')} for assoc in associations}
        except json.JSONDecodeError as e:
            print(f"JSON 디코딩 오류 발생: {e}")
            return {}
        except Exception as e:
            print(f"기타 오류 발생: {e}")
            return {}

    rt_dict = {}
    for _, row in rt_df.iterrows():
        rt_dict.update(parse_associations(row['Associations']))

    # Network ACL 정보를 딕셔너리 형태로 변환
    def parse_network_acl_associations(json_str):
        try:
            associations = json.loads(json_str)
            return {assoc.get('SubnetId', ''): {'Network Acl ID': assoc.get('NetworkAclId', ''), 'Title': assoc.get('NetworkAclAssociationId', '')} for assoc in associations}
        except json.JSONDecodeError as e:
            print(f"JSON 디코딩 오류 발생: {e}")
            return {}

    nacl_dict = {}
    for _, row in network_acl_df.iterrows():
        nacl_dict.update(parse_network_acl_associations(row['Associations']))

    # Subnet Type 열 계산 (Subnet Name 네 번째 대시 뒤의 단어)
    def extract_subnet_type(subnet_name):
        parts = subnet_name.split('-')
        if parts[4] == 'pri':
            return 'private'
        elif parts[4] == 'pub':
            return 'public'
        else:
            return parts[4]

    # Route Table ID와 Route Table Name을 각각 반환
    def get_route_table_id(subnet_id):
        if subnet_id in rt_dict:
            return rt_dict[subnet_id]['Route Table ID']
        return ''

    def get_route_table_name(subnet_id):
        if subnet_id in rt_dict:
            return rt_dict[subnet_id]['Title']
        return ''

    # Network ACL ID와 Network ACL Name을 각각 반환
    def get_network_acl_id(subnet_id):
        if subnet_id in nacl_dict:
            return nacl_dict[subnet_id]['Network Acl ID']
        return ''

    def get_network_acl_name(subnet_id):
        # nacl_dict에서 'Title'을 Network ACL Name으로 사용
        return nacl_dict.get(subnet_id, {}).get('Title', '')

    # 변환된 데이터 프레임 생성
    transformed_df = pd.DataFrame({
        'Subnet ID': subnet_df['Subnet ID'],
        'Subnet Name': subnet_df['Title'],
        # 'Subnet Type': subnet_df['Title'].apply(extract_subnet_type),
        'Subnet CIDR Block': subnet_df['Cidr Block'],
        'Availability Zone': subnet_df['Availability Zone'],
        'Route Table ID': subnet_df['Subnet ID'].apply(get_route_table_id),
        'Route Table Name': subnet_df['Subnet ID'].apply(get_route_table_name),
        'Network ACL ID': subnet_df['Subnet ID'].apply(get_network_acl_id),
        'Network ACL Name': subnet_df['Subnet ID'].apply(get_network_acl_name),
        'Compared with Last Month': '-'
    })

    return transformed_df

def load_and_transform_subnet_data(subnet_csv_file, rt_csv_file, network_acl_csv_file):
    return transform_subnet_data(subnet_csv_file, rt_csv_file, network_acl_csv_file)
