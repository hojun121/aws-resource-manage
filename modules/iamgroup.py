import pandas as pd
import json

def extract_policies(policy_column):
    """정책 정보를 추출하여 알파벳 순서로 정렬된 콤마로 구분된 문자열로 반환합니다.
    arn:aws:iam:: 부분은 제거합니다.
    """
    try:
        if pd.isna(policy_column) or not policy_column.strip():
            return '-'

        policies = json.loads(policy_column)

        # 정책 문자열에서 'arn:aws:iam::' 부분 제거
        cleaned_policies = [policy.replace('arn:aws:iam::', '') for policy in policies]

        # 정책 정보를 알파벳 순서로 정렬
        sorted_policies = sorted(cleaned_policies)

        return ', '.join(policy for policy in sorted_policies)

    except json.JSONDecodeError as e:
        print(f"JSON 디코딩 오류 발생: {e}")
        return '-'
    except Exception as e:
        print(f"기타 오류 발생: {e}")
        return '-'

def transform_iam_group_data(iam_group_csv_file):
    """IAM 그룹 데이터를 변환하여 DataFrame으로 반환합니다."""
    csv_data = pd.read_csv(iam_group_csv_file, encoding='utf-8')
    csv_data = csv_data.fillna('')

    # 변환된 데이터프레임 생성
    transformed_data = pd.DataFrame({
        'Group Name': csv_data['Name'],
        'IAM Policy': csv_data['Attached Policy Arns'].apply(extract_policies),
        'Compared with Last Month': '-'
    })

    return transformed_data

def load_and_transform_iam_group_data(iam_group_csv_file):
    return transform_iam_group_data(iam_group_csv_file)
