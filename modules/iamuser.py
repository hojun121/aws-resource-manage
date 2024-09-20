import pandas as pd
import json

import json
import pandas as pd


def format_groups(groups_column):
    """IAM 그룹 정보를 콤마로 구분된 문자열로 반환합니다."""
    try:
        if pd.isna(groups_column) or not groups_column.strip():
            return '-'

        groups = json.loads(groups_column)

        if isinstance(groups, list):
            if all(isinstance(item, dict) for item in groups):
                return ', '.join(item.get('GroupName', 'Unknown') for item in groups) if groups else '-'
            else:
                print(f"예상치 못한 그룹 형식: {groups_column}")
                return '-'
        else:
            print(f"예상치 못한 JSON 형식: {groups_column}")
            return '-'
    except json.JSONDecodeError as e:
        print(f"JSON 디코딩 오류 발생: {e}")
        return '-'
    except Exception as e:
        print(f"기타 오류 발생: {e}")
        return '-'


def format_mfa_enabled(mfa_column):
    """MFA 활성화 여부를 'Y' 또는 'N'으로 반환합니다."""
    try:
        # 값이 None 또는 빈 문자열인 경우 '-' 반환
        if pd.isna(mfa_column):
            return '-'

        # `mfa_column` 값을 문자열로 변환한 후 소문자 비교
        if isinstance(mfa_column, bool):
            return 'Y' if mfa_column else 'N'
        elif isinstance(mfa_column, str):
            return 'Y' if mfa_column.lower() == 'true' else 'N'
        else:
            print(f"예상치 못한 MFA 활성화 값: {mfa_column}")
            return '-'
    except Exception as e:
        print(f"MFA 처리 중 오류 발생: {e}")
        return '-'


def transform_iam_user_data(iam_user_csv_file):
    """IAM 사용자 데이터를 변환하여 DataFrame으로 반환합니다."""
    csv_data = pd.read_csv(iam_user_csv_file, encoding='utf-8')
    csv_data = csv_data.fillna('')

    transformed_data = pd.DataFrame({
        'User Name': csv_data['Name'],
        'IAM Group': csv_data['Groups'].apply(format_groups),
        'MFA Credential Y/N': csv_data['Mfa Enabled'].apply(format_mfa_enabled),
        'Creation Time': csv_data['Create Date'],
        'Compared with Last Month': '-'
    })

    return transformed_data


def load_and_transform_iam_user_data(iam_user_csv_file):
    return transform_iam_user_data(iam_user_csv_file)
