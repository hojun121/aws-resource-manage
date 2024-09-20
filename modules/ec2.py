import pandas as pd
import json


def extract_group_id(security_groups):
    """보안 그룹의 ID를 추출합니다."""
    try:
        if pd.isna(security_groups) or not security_groups.strip():
            return ''

        groups = json.loads(security_groups)
        return ', '.join(group.get('GroupId', '') for group in groups)
    except json.JSONDecodeError as e:
        print(f"JSON 디코딩 오류 발생: {e}")
        return ''
    except Exception as e:
        print(f"기타 오류 발생: {e}")
        return ''


def format_tags(tags):
    """태그를 알파벳 순서로 정렬하여 형식화합니다. 빈 태그는 '-'로 표기합니다."""
    try:
        # 태그 데이터가 None이거나 빈 문자열인 경우 '-' 반환
        if pd.isna(tags) or not tags.strip():
            return '-'

        # JSON 파싱 시도
        tag_dict = json.loads(tags)

        # 태그가 딕셔너리 형태일 때
        if isinstance(tag_dict, dict):
            # 딕셔너리의 키-값 쌍을 알파벳 순서로 정렬
            sorted_tags = sorted(tag_dict.items(), key=lambda item: item[0])

            # 알파벳 순서로 정렬된 태그를 형식화
            formatted_tags = ', '.join(f"{k}: {v}" for k, v in sorted_tags)
            return formatted_tags if formatted_tags else '-'

        else:
            # 예상치 못한 형식일 때
            print(f"예상치 못한 JSON 형식: {tags}")
            return '-'

    except json.JSONDecodeError as e:
        print(f"JSON 디코딩 오류 발생: {e}")
        return '-'
    except Exception as e:
        print(f"태그 처리 중 예상치 못한 오류 발생: {e}")
        return '-'


def transform_ec2_data(ec2_csv_file):
    """EC2 인스턴스 데이터를 변환합니다."""
    # CSV 파일을 DataFrame으로 읽기
    csv_data = pd.read_csv(ec2_csv_file, encoding='utf-8')

    # 각 열에 대해 NaN 또는 빈 값 처리
    csv_data = csv_data.fillna('')

    # DataFrame 생성
    transformed_data = pd.DataFrame({
        'Instance State': csv_data['Instance State'],
        'Region': csv_data['Region'],
        'Availability Zone': csv_data['Placement Availability Zone'],
        'SEV': '-',
        'Instance Name': csv_data['Title'],
        'Instance ID': csv_data['Instance ID'],
        'Image ID': csv_data['Image ID'],
        'Instance Type': csv_data['Instance Type'],
        'Vpc ID': csv_data['Vpc ID'],
        'Subnet ID': csv_data['Subnet ID'],
        'Private IP Address': csv_data['Private IP Address'],
        'Root Device Type': csv_data['Root Device Type'],
        'Security Groups': csv_data['Security Groups'].apply(extract_group_id),
        'Key Name': csv_data['Key Name'],
        'Tags': csv_data['Tags'].apply(format_tags),
        'Compared with Last Month': '-'
    })

    return transformed_data


def load_and_transform_ec2_data(ec2_csv_file):
    return transform_ec2_data(ec2_csv_file)
