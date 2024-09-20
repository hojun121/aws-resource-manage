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

        return ', '.join(sorted_policies)

    except json.JSONDecodeError as e:
        print(f"JSON 디코딩 오류 발생: {e}")
        return '-'
    except Exception as e:
        print(f"기타 오류 발생: {e}")
        return '-'


def format_principals(principal_column):
    """Principal 정보를 Key: Value, Key, Value 형태로 변환합니다. 빈 데이터는 '-'로 표기합니다."""
    try:
        # Principal 데이터가 None이거나 빈 문자열인 경우 '-' 반환
        if pd.isna(principal_column) or not principal_column.strip():
            return '-'

        # JSON 문자열을 파싱하여 객체로 변환
        assume_role_policy = json.loads(principal_column)

        # Principal 정보를 추출하여 Key: Value, Key, Value 형식으로 변환
        principals = []
        for statement in assume_role_policy.get('Statement', []):
            principal = statement.get('Principal', {})
            if isinstance(principal, dict):
                for key, value in principal.items():
                    # 각 Key-Value 쌍을 변환하여 리스트에 추가
                    principals.append(f"{key}: {value}")  # Key:Value 형식

        return ', '.join(map(str, principals)) if principals else '-'

    except json.JSONDecodeError as e:
        print(f"JSON 디코딩 오류 발생: {e}")
        return '-'
    except Exception as e:
        print(f"Principal 처리 중 예상치 못한 오류 발생: {e}")
        return '-'


def transform_iam_role_data(iam_role_csv_file):
    """IAM Role 데이터를 변환하여 DataFrame으로 반환합니다."""
    csv_data = pd.read_csv(iam_role_csv_file, encoding='utf-8')
    csv_data = csv_data.fillna('')

    transformed_data = pd.DataFrame({
        'Role Name': csv_data['Name'],
        'Trusted Entities': csv_data['Assume Role Policy'].apply(format_principals),
        'Policy(arn:aws:iam::)': csv_data['Attached Policy Arns'].apply(extract_policies),
        'Compared with Last Month': '-'
    })

    return transformed_data


def load_and_transform_iam_role_data(iam_role_csv_file):
    return transform_iam_role_data(iam_role_csv_file)
