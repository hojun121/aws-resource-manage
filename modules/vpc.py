import pandas as pd
import json


def transform_vpc_data(vpc_data, igw_data, ngw_data):

    def extract_vpc_id(attachments):
        try:
            # JSON이 파싱된 상태로 처리하므로, 이미 리스트로 되어 있다면 직접 접근
            if isinstance(attachments, list) and len(attachments) > 0:
                return attachments[0].get('VpcId', '')  # 리스트의 첫 번째 요소에서 'VpcId' 추출
            else:
                return ''
        except Exception as e:
            print(f"오류 발생: {e}")
            return ''

    igw_data['vpc_id'] = igw_data['attachments'].apply(extract_vpc_id)
    igw_data['igw_title'] = igw_data['title']
    ngw_data['vpc_id'] = ngw_data['vpc_id']

    # VPC와 Internet Gateway 데이터를 매핑
    vpc_data = vpc_data.merge(igw_data[['vpc_id', 'internet_gateway_id', 'igw_title']],
                              on='vpc_id', how='left')

    # VPC와 NAT Gateway 데이터를 매핑
    vpc_data = vpc_data.merge(ngw_data[['vpc_id', 'nat_gateway_id']],
                              on='vpc_id', how='left')

    # 인터넷 게이트웨이 ID를 그룹화하여 결합
    vpc_data['internet_gateway_ids'] = vpc_data.groupby('vpc_id')['internet_gateway_id'].transform(
        lambda x: ', '.join(x.dropna().astype(str)) if not x.dropna().empty else "None"
    )

    # NAT 게이트웨이 ID를 그룹화하여 결합
    vpc_data['nat_gateway_ids'] = vpc_data.groupby('vpc_id')['nat_gateway_id'].transform(
        lambda x: ', '.join(x.dropna().astype(str)) if not x.dropna().empty else "None"
    )

    # DNS Resolution과 DNS Hostname을 빈 문자열로 설정
    vpc_data['DNS Resolution'] = "(Type Here)"
    vpc_data['DNS Hostname'] = "(Type Here)"

    # VPC 데이터에서 중복 VPC ID 제거
    vpc_data = vpc_data.drop_duplicates(subset='vpc_id')

    # 최종 변환된 데이터 생성
    transformed_data = pd.DataFrame({
        'Name': vpc_data['title'],
        'ID': vpc_data['vpc_id'],
        'VPC CIDR Block': vpc_data['cidr_block'],
        'NAT Gateway': vpc_data['nat_gateway_ids'],
        'Internet Gateways Name': vpc_data['igw_title'],
        'Internet Gateways ID': vpc_data['internet_gateway_ids'],
        'DNS Resolution': vpc_data['DNS Resolution'],
        'DNS Hostname': vpc_data['DNS Hostname']
    })

    # Sort VPC by VPC Name in Desc
    transformed_data = transformed_data.sort_values(by='Name', ascending=False)

    return transformed_data


def load_and_transform_vpc_data(vpc_data, igw_data, ngw_data):
    return transform_vpc_data(vpc_data, igw_data, ngw_data)
