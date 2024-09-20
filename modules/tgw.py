import pandas as pd
import json


def transform_tgw_data(tgw_csv_file):
    """TGW 데이터를 변환합니다."""
    # CSV 파일을 DataFrame으로 읽어옵니다
    csv_data = pd.read_csv(tgw_csv_file, encoding='utf-8')
    csv_data = csv_data.fillna('')  # NaN 값을 빈 문자열로 대체합니다

    # 선택된 열과 변환된 데이터를 포함한 새로운 DataFrame 생성
    transformed_data = pd.DataFrame({
        'Transit Gateway ID': csv_data['Transit Gateway ID'],
        'Name': csv_data['Title'],
        'State': csv_data['State'],
        'Region': csv_data['Region'],
        'Default Association Route Table': csv_data['Default Route Table Association'],
        'Default Propagation Route Table': csv_data['Default Route Table Propagation'],
        'Transit Gateway CIDR Blocks': csv_data['Cidr Blocks'].apply(lambda x: '-' if not x else x),
        'Association Route Table ID': csv_data['Association Default Route Table ID'].apply(lambda x: '-' if not x else x),
        'Propagation Route Table ID': csv_data['Propagation Default Route Table ID'].apply(lambda x: '-' if not x else x),
        'Multicast Support': csv_data['Multicast Support'],
        'DNS Support': csv_data['Dns Support'],
        'Auto Accept Shared Attachments': csv_data['Auto Accept Shared Attachments'],
        'VPN ECMP Support': csv_data['Vpn Ecmp Support'],
        'Compared with Last Month': '-'
    })

    return transformed_data


def load_and_transform_tgw_data(tgw_csv_file):
    """TGW 데이터를 로드하고 변환합니다."""
    return transform_tgw_data(tgw_csv_file)
