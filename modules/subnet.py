import pandas as pd
import json

def transform_subnet_data(subnet_data, rt_data, nacl_data):

    def parse_rf_associations(associations):
        try:
            return {assoc.get('SubnetId', ''): {'Route Table ID': assoc.get('RouteTableId', ''), 'Title': assoc.get('RouteTableAssociationId', '')} for assoc in associations}
        except json.JSONDecodeError as e:
            print(f"JSON 디코딩 오류 발생: {e}")
            return {}
        except Exception as e:
            print(f"기타 오류 발생: {e}")
            return {}

    def parse_network_acl_associations(associations):
        try:
            return {assoc.get('SubnetId', ''): {'Network Acl ID': assoc.get('NetworkAclId', ''), 'Title': assoc.get('NetworkAclAssociationId', '')} for assoc in associations}
        except Exception as e:
            print(f"기타 오류 발생: {e}")
            return {}

    def extract_subnet_type(subnet_name):
        try:
            parts = subnet_name.split('-')
            if len(parts) > 4:
                if parts[4] == 'pri':
                    return 'private'
                elif parts[4] == 'pub':
                    return 'public'
                else:
                    return parts[4]
            else:
                return ''
        except Exception as e:
            print(f"Subnet type 추출 오류: {e}")
            return ''

    def get_route_table_id(subnet_id):
        if subnet_id in rt_dict:
            return rt_dict[subnet_id]['Route Table ID']
        return ''

    def get_route_table_name(subnet_id):
        if subnet_id in rt_dict:
            return rt_dict[subnet_id]['Title']
        return ''

    def get_network_acl_id(subnet_id):
        if subnet_id in nacl_dict:
            return nacl_dict[subnet_id]['Network Acl ID']
        return ''

    def get_network_acl_name(subnet_id):
        return nacl_dict.get(subnet_id, {}).get('Title', '')

    def get_igw_or_nat(subnet_type):
        if subnet_type == 'public':
            return 'IGW'
        return ''

    rt_dict = {}
    for _, row in rt_data.iterrows():
        associations = row['associations']
        rt_dict.update(parse_rf_associations(associations))

    nacl_dict = {}
    for _, row in nacl_data.iterrows():
        associations = row['associations']
        nacl_dict.update(parse_network_acl_associations(associations))

    transformed_data = pd.DataFrame({
        'Name': subnet_data['title'],
        'ID': subnet_data['subnet_id'],
        'Subnet Type': subnet_data['title'].apply(extract_subnet_type),
        'IGW/NAT': subnet_data['title'].apply(extract_subnet_type).apply(get_igw_or_nat),
        'Subnet CIDR Block': subnet_data['cidr_block'],
        'Availability Zone': subnet_data['availability_zone'],
        'Route Table ID': subnet_data['subnet_id'].apply(get_route_table_id),
        'Route Table Name': subnet_data['subnet_id'].apply(get_route_table_name),
        'Network ACL ID': subnet_data['subnet_id'].apply(get_network_acl_id),
        'Network ACL Name': subnet_data['subnet_id'].apply(get_network_acl_name),
    })

    transformed_data = transformed_data.sort_values(by='Name', ascending=False)

    return transformed_data

def load_and_transform_subnet_data(subnet_data, rt_data, nacl_data):
    return transform_subnet_data(subnet_data, rt_data, nacl_data)
