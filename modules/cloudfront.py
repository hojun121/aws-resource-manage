import pandas as pd
import json


def extract_json_value(json_string, key):
    """JSON 문자열에서 특정 키의 값을 추출합니다."""
    try:
        if pd.isna(json_string) or not json_string.strip():
            return ''

        data = json.loads(json_string)
        if isinstance(data, dict):
            # 'Items' 키의 값을 추출
            if key == 'Items' and isinstance(data.get(key), list):
                return ', '.join(data[key])
            return data.get(key, '')
        elif isinstance(data, list):
            # 리스트의 경우, 리스트의 모든 항목을 문자열로 변환하여 반환
            return ', '.join(str(item) for item in data)
        else:
            return ''
    except json.JSONDecodeError as e:
        print(f"JSON 디코딩 오류 발생: {e}")
        return ''
    except Exception as e:
        print(f"기타 오류 발생: {e}")
        return ''


def extract_domain_name_from_origins(json_string):
    """Origins JSON 문자열에서 DomainName 값을 추출합니다."""
    try:
        if pd.isna(json_string) or not json_string.strip():
            return ''

        data = json.loads(json_string)
        if isinstance(data, list):
            domain_names = [item.get('DomainName', '') for item in data if 'DomainName' in item]
            return ', '.join(domain_names)
        return ''
    except json.JSONDecodeError as e:
        print(f"JSON 디코딩 오류 발생: {e}")
        return ''
    except Exception as e:
        print(f"기타 오류 발생: {e}")
        return ''


def transform_cloudfront_data(cloudfront_csv_file):
    """CloudFront 배포 데이터를 변환합니다."""
    # CSV 파일을 DataFrame으로 읽기
    csv_data = pd.read_csv(cloudfront_csv_file, encoding='utf-8')

    # 각 열에 대해 NaN 또는 빈 값 처리
    csv_data = csv_data.fillna('')

    # DataFrame 생성
    transformed_data = pd.DataFrame({
        'ID': csv_data['ID'],
        'Domain Name': csv_data['Domain Name'],
        'Alternate Domain Name': csv_data['Aliases'].apply(lambda x: extract_json_value(x, 'Items')),
        'Origin': csv_data['Origins'].apply(extract_domain_name_from_origins),
        'SSL Certificate': csv_data['Viewer Certificate'].apply(lambda x: extract_json_value(x, 'Certificate')),
        'Description': csv_data['Comment'],
        'Compared with Last Month': '-'
    })

    return transformed_data


def load_and_transform_cloudfront_data(cloudfront_csv_file):
    return transform_cloudfront_data(cloudfront_csv_file)
