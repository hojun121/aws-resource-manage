import pandas as pd
import json


def parse_availability_zones(availability_zones):
    """가용 영역 JSON을 파싱하여 쉼표로 구분된 문자열로 반환합니다."""
    try:
        if pd.isna(availability_zones) or not availability_zones.strip():
            return ''
        zones = json.loads(availability_zones)
        return ', '.join([zone['ZoneName'] for zone in zones if 'ZoneName' in zone])
    except json.JSONDecodeError as e:
        print(f"가용 영역 JSON 디코딩 오류: {e}")
        return ''
    except Exception as e:
        print(f"가용 영역 파싱 중 예상치 못한 오류 발생: {e}")
        return ''


def parse_security_groups(security_groups):
    """보안 그룹 JSON을 파싱하여 쉼표로 구분된 문자열로 반환합니다."""
    try:
        if pd.isna(security_groups) or not security_groups.strip():
            return ''
        groups = json.loads(security_groups)
        return ', '.join(groups)
    except json.JSONDecodeError as e:
        print(f"보안 그룹 JSON 디코딩 오류: {e}")
        return ''
    except Exception as e:
        print(f"보안 그룹 파싱 중 예상치 못한 오류 발생: {e}")
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


def transform_load_balancer_data(csv_file, elb_type):
    """로드 밸런서 데이터를 변환합니다."""
    # CSV 파일을 DataFrame으로 읽어옵니다
    data = pd.read_csv(csv_file, encoding='utf-8')
    data = data.fillna('')  # NaN 값을 빈 문자열로 대체합니다

    # 필요한 열과 변환된 데이터를 포함한 새로운 DataFrame 생성
    transformed_data = pd.DataFrame({
        'State Code': data['State Code'],  # State Code 값을 그대로 사용
        'Region': data['Region'],
        'Scheme': data['Scheme'],
        'ELB Name': data['Name'],
        'DNS Name': data['Dns Name'],
        'Type': elb_type,
        # 'Availability Zone': data['Availability Zones'].apply(parse_availability_zones),
        'ELB Security Group': data['Security Groups'].apply(parse_security_groups),
        'Cross-Zone Load Balancing': data['Load Balancer Attributes'].apply(
            lambda x: 'Yes' if 'cross_zone' in str(x).lower() and 'true' in str(x).lower() else ''),
        'Access Logs': data['Load Balancer Attributes'].apply(
            lambda x: 'Yes' if 'access_logs.s3.enabled' in str(x).lower() and 'true' in str(x).lower() else ''),
        'Tag': data['Tags'].apply(format_tags),
        'Compared with Last Month': '-'
    })

    return transformed_data


def load_and_transform_elb_data(alb_csv_file, nlb_csv_file):
    # 빈 리스트를 생성하여 변환된 데이터를 추가할 준비
    data_frames = []

    # ALB 데이터 변환 (파일이 존재하는 경우에만)
    if alb_csv_file is not None:
        alb_data = transform_load_balancer_data(alb_csv_file, 'application')
        data_frames.append(alb_data)

    # NLB 데이터 변환 (파일이 존재하는 경우에만)
    if nlb_csv_file is not None:
        nlb_data = transform_load_balancer_data(nlb_csv_file, 'network')
        data_frames.append(nlb_data)

    # 존재하는 데이터만 결합
    combined_data = pd.concat(data_frames, ignore_index=True) if data_frames else pd.DataFrame()

    return combined_data

