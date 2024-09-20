import pandas as pd
import json


def check_availability_zones(azs):
    """Availability Zones이 있는지 확인하여 'Yes' 또는 'No' 반환"""
    return 'Yes' if pd.notna(azs) and azs.strip() and azs != '[]' else 'No'


def extract_target_health_states(json_string):
    """Target Health Descriptions JSON 문자열에서 State 값을 추출하여 상태를 평가합니다."""
    try:
        if pd.isna(json_string) or not json_string.strip():
            return ''

        data = json.loads(json_string)
        if isinstance(data, list):
            states = [item.get('TargetHealth', {}).get('State', '') for item in data]

            if not states:
                return ''
            if all(state == 'healthy' for state in states):
                return 'healthy'
            elif any(state == 'unhealthy' for state in states):
                return 'partially unhealthy'
            else:
                return 'unknown'
        return ''
    except json.JSONDecodeError as e:
        print(f"JSON 디코딩 오류 발생: {e}")
        return ''
    except Exception as e:
        print(f"기타 오류 발생: {e}")
        return ''


def transform_target_group_data(target_group_csv_file):
    """Target Groups CSV 데이터를 변환하여 필요한 정보를 추출"""
    # CSV 파일을 DataFrame으로 읽기
    csv_data = pd.read_csv(target_group_csv_file, encoding='utf-8')

    # csv_data가 DataFrame인 경우, 각 열에 대해 NaN 또는 빈 값 처리
    csv_data = csv_data.fillna('')

    # DataFrame 생성
    transformed_data = pd.DataFrame({
        'Name': csv_data['Target Group Name'],
        'Protocol': csv_data['Protocol'],
        'Target Type': csv_data['Target Type'],
        'Load Balancer': csv_data['Load Balancer Arns'].apply(lambda x: ', '.join(json.loads(x)) if pd.notna(x) and x.strip() else ''),
        'VPC ID': csv_data['Vpc ID'],
        'Healthy Threshold Count': csv_data['Healthy Threshold Count'],
        'Unhealthy Threshold Count': csv_data['Unhealthy Threshold Count'],
        'Health Check Enabled': csv_data['Health Check Enabled'],
        'Health Check Interval Seconds': csv_data['Health Check Interval Seconds'],
        'Health Check Path': csv_data['Health Check Path'],
        'Health Check Port': csv_data['Health Check Port'],
        'Health Check Protocol': csv_data['Health Check Protocol'],
        'Health Check Timeout Seconds': csv_data['Health Check Timeout Seconds'],
        'Target Health States': csv_data['Target Health Descriptions'].apply(extract_target_health_states),
        'Compared with Last Month': '-'
    })

    return transformed_data


def load_and_transform_target_group_data(target_group_csv_file):
    return transform_target_group_data(target_group_csv_file)
