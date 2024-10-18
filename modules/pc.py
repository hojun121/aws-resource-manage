import pandas as pd

def extract_cidr(cidr_set):
    # cidr_set이 리스트라면 각 항목에서 'CidrBlock' 값을 추출
    if isinstance(cidr_set, list):
        # cidr_set 내의 각 항목이 딕셔너리라면 'CidrBlock' 키의 값을 추출
        return ', '.join([entry['CidrBlock'] if isinstance(entry, dict) and 'CidrBlock' in entry else '' for entry in cidr_set])
    else:
        return 'None'


# Peering Connection 데이터 변환 함수
def transform_pc_data(pc_data):
    # CIDR 블록 변환
    pc_data['requester_cidrs'] = pc_data['requester_cidr_block_set'].apply(extract_cidr)
    pc_data['accepter_cidrs'] = pc_data['accepter_cidr_block_set'].apply(extract_cidr)

    transformed_data = pd.DataFrame({
        'Name': pc_data['title'],
        'ID': pc_data['id'],
        'State': pc_data['status_code'],
        'Requester VPC': pc_data['requester_vpc_id'],
        'Accepter VPC': pc_data['accepter_vpc_id'],
        'Requester CIDRs': pc_data['requester_cidrs'],
        'Accepter CIDRs': pc_data['accepter_cidrs'],
        'Requester owner ID': pc_data['requester_owner_id'],
        'Accepter owner ID': pc_data['accepter_owner_id'],
        'Requester Region': pc_data['requester_region'],
        'Accepter Region': pc_data['accepter_region'],
    })

    transformed_data = transformed_data.sort_values(by='Name', ascending=False)

    return transformed_data

def load_and_transform_pc_data(pc_data):
    return transform_pc_data(pc_data)
