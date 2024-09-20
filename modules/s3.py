import pandas as pd
import json


def extract_policy_info(policy_column):
    """정책 정보를 추출하여 콤마로 구분된 문자열로 반환합니다."""
    try:
        if pd.isna(policy_column) or not policy_column.strip():
            return ''
        policies = json.loads(policy_column)

        # 새로운 정책 정보를 저장할 리스트
        policy_info = []

        if isinstance(policies, dict):
            for statement in policies.get('Statement', []):
                # Principal 키 제거
                principal = statement.get('Principal', {})
                if isinstance(principal, dict):
                    principal_info = ', '.join(f"{key}: {value}" for key, value in principal.items())
                    policy_info.append(principal_info)
                else:
                    policy_info.append(str(principal))
            return ', '.join(policy_info) if policy_info else ''

        elif isinstance(policies, list):
            return ', '.join(str(policy) for policy in policies)

        return str(policies)
    except json.JSONDecodeError as e:
        print(f"JSON 디코딩 오류 발생: {e}")
        return ''
    except TypeError as e:
        print(f"타입 오류 발생: {e}")
        return ''
    except Exception as e:
        print(f"기타 오류 발생: {e}")
        return ''

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

def extract_expire_days(json_string):
    """Lifecycle Rules JSON 문자열에서 Expiration Days 값을 추출합니다."""
    try:
        if pd.isna(json_string) or not json_string.strip():
            return ''

        data = json.loads(json_string)
        if isinstance(data, dict):
            data = data.get('Rules', [])
        if isinstance(data, list):
            expire_days = []
            for rule in data:
                expiration = rule.get('Expiration', {})
                days = expiration.get('Days', '')
                if days:
                    expire_days.append(str(days))
            return ', '.join(expire_days)
        return ''
    except json.JSONDecodeError as e:
        print(f"JSON 디코딩 오류 발생: {e}")
        return ''
    except Exception as e:
        print(f"기타 오류 발생: {e}")
        return ''

def extract_target_bucket(logging_data):
    """Logging 데이터에서 TargetBucket 값을 추출합니다."""
    try:
        if pd.isna(logging_data) or not logging_data.strip():
            return '-'

        # JSON 문자열을 파싱
        data = json.loads(logging_data)

        # TargetBucket 값을 추출
        target_bucket = data.get('TargetBucket', '-')
        return target_bucket
    except json.JSONDecodeError as e:
        print(f"JSON 디코딩 오류 발생: {e}")
        return '-'
    except Exception as e:
        print(f"기타 오류 발생: {e}")
        return '-'

def transform_s3_data(s3_csv_file):
    """S3 데이터를 변환하여 DataFrame으로 반환합니다."""
    csv_data = pd.read_csv(s3_csv_file, encoding='utf-8')
    csv_data = csv_data.fillna('')

    transformed_data = pd.DataFrame({
        'Region': csv_data['Region'],
        'Bucket Name': csv_data['Name'],
        'Block All Public Access': csv_data[
            ['Block Public Acls', 'Block Public Policy', 'Ignore Public Acls', 'Restrict Public Buckets']].apply(
            lambda x: 'Yes' if all(x == 'true') else 'No', axis=1),
        'Versioning': csv_data['Versioning Enabled'],
        'Encryption': csv_data['Server Side Encryption Configuration'].apply(
            lambda x: 'Yes' if pd.notna(x) and x.strip() else 'No'),
        'Static Web Hosting': csv_data['Website Configuration'].apply(
            lambda x: 'Yes' if pd.notna(x) and x.strip() else 'No'),  # 수정된 부분
        'Bucket Policy': csv_data['Policy'].apply(extract_policy_info),
        'Lifecycle Expire Days': csv_data['Lifecycle Rules'].apply(extract_expire_days),
        'Static Log': csv_data['Logging'].apply(extract_target_bucket),  # Updated to use extract_target_bucket
        'Tag': csv_data['Tags'].apply(format_tags),
        'Compared with Last Month': '-'
    })

    return transformed_data

def load_and_transform_s3_data(s3_csv_file):
    return transform_s3_data(s3_csv_file)
