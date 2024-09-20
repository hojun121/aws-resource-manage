import pandas as pd
import json


def extract_instances(instances):
    """인스턴스 JSON 열에서 인스턴스 정보를 추출합니다."""
    try:
        if pd.isna(instances) or not instances.strip():
            return ''

        instance_list = json.loads(instances)
        return ', '.join([f"{instance.get('InstanceId', '')} ({instance.get('LifecycleState', '')})"
                          for instance in instance_list])
    except json.JSONDecodeError as e:
        print(f"JSON 디코딩 오류: {e}")
        return ''
    except Exception as e:
        print(f"예상치 못한 오류 발생: {e}")
        return ''


def extract_launch_template(row):
    """런치 템플릿 또는 구성의 세부 정보를 결합합니다."""
    if row['Launch Template Name']:
        return f"{row['Launch Template Name']} (Version: {row['Launch Template Version']})"
    elif row['Launch Configuration Name']:
        return row['Launch Configuration Name']
    return ''


def transform_autoscaling_data(autoscaling_csv_file):
    """오토스케일링 데이터를 변환합니다."""
    # CSV 파일을 DataFrame으로 읽어옵니다
    csv_data = pd.read_csv(autoscaling_csv_file, encoding='utf-8')
    csv_data = csv_data.fillna('')  # NaN 값을 빈 문자열로 대체합니다

    # 선택된 열과 변환된 데이터를 포함한 새로운 DataFrame 생성
    transformed_data = pd.DataFrame({
        'Name': csv_data['Name'],
        'Launch template/configuration': csv_data.apply(extract_launch_template, axis=1),
        'Instances': csv_data['Instances'].apply(extract_instances),
        'Desired Capacity': csv_data['Desired Capacity'],
        'Min': csv_data['Min Size'],
        'Max': csv_data['Max Size'],
        'Compared with Last Month': '-'
        # 'AZ': csv_data['Availability Zones'].apply(lambda x: ', '.join(json.loads(x)) if x else '') 필수
    })

    return transformed_data


def load_and_transform_autoscaling_data(autoscaling_csv_file):
    return transform_autoscaling_data(autoscaling_csv_file)
