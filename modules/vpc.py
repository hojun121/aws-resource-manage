import pandas as pd
import json


def transform_vpc_data(vpc_csv_file, igw_csv_file):
    # CSV 파일을 DataFrame으로 읽기
    vpc_data = pd.read_csv(vpc_csv_file, encoding='utf-8')
    igw_data = pd.read_csv(igw_csv_file, encoding='utf-8')

    # Internet Gateway 데이터에서 VPC ID와 Internet Gateway ID를 추출
    def extract_vpc_id_from_attachments(attachments):
        try:
            attachments_list = json.loads(attachments)
            if attachments_list:
                return attachments_list[0].get('VpcId', '')
        except json.JSONDecodeError as e:
            print(f"JSON 디코딩 오류 발생: {e}")
            return ''
        except Exception as e:
            print(f"기타 오류 발생: {e}")
            return ''

    igw_data['Vpc ID'] = igw_data['Attachments'].apply(extract_vpc_id_from_attachments)

    # VPC와 Internet Gateway 데이터를 매핑
    vpc_data = vpc_data.merge(igw_data[['Vpc ID', 'Internet Gateway ID']],
                              on='Vpc ID', how='left')

    # 변환된 데이터 프레임을 생성
    transformed_data = pd.DataFrame({
        'VPC Name': vpc_data['Title'],
        'VPC ID': vpc_data['Vpc ID'],
        'VPC CIDR Block': vpc_data['Cidr Block'],
        'Internet Gateways ID': vpc_data['Internet Gateway ID'].fillna(''),
        'DNS Hostname': '-',
        'Compared with Last Month': '-'
    })

    return transformed_data


def load_and_transform_vpc_data(vpc_csv_file, igw_csv_file):
    return transform_vpc_data(vpc_csv_file, igw_csv_file)
