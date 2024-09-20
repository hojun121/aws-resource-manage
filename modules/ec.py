import pandas as pd
import json


def format_security_groups(security_groups):
    """보안 그룹의 ID를 추출합니다."""
    try:
        if pd.isna(security_groups) or not security_groups.strip():
            return ''

        groups = json.loads(security_groups)
        return ', '.join(group.get('SecurityGroupId', '') for group in groups)
    except json.JSONDecodeError as e:
        print(f"JSON 디코딩 오류 발생: {e}")
        return ''
    except Exception as e:
        print(f"기타 오류 발생: {e}")
        return ''


def format_tags(tags):
    """태그를 알파벳 순서로 정렬하여 형식화합니다. 빈 태그는 '-'로 표기합니다."""
    try:
        if pd.isna(tags) or not tags.strip():
            return '-'

        tag_dict = json.loads(tags)
        if isinstance(tag_dict, dict):
            sorted_tags = sorted(tag_dict.items(), key=lambda item: item[0])
            formatted_tags = ', '.join(f"{k}: {v}" for k, v in sorted_tags)
            return formatted_tags if formatted_tags else '-'
        else:
            print(f"예상치 못한 JSON 형식: {tags}")
            return '-'
    except json.JSONDecodeError as e:
        print(f"JSON 디코딩 오류 발생: {e}")
        return '-'
    except Exception as e:
        print(f"태그 처리 중 예상치 못한 오류 발생: {e}")
        return '-'


def extract_endpoints(node_groups):
    """Primary와 Reader Endpoints를 추출합니다."""
    try:
        groups = json.loads(node_groups)
        if not groups or not isinstance(groups, list) or len(groups) == 0:
            return '', ''

        primary_endpoint = groups[0].get('PrimaryEndpoint')
        reader_endpoint = groups[0].get('ReaderEndpoint')

        # Primary와 Reader Endpoints가 None일 경우 빈 문자열로 처리
        primary_endpoint_address = primary_endpoint.get('Address', '') if primary_endpoint else ''
        reader_endpoint_address = reader_endpoint.get('Address', '') if reader_endpoint else ''

        return primary_endpoint_address, reader_endpoint_address
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        print(f"엔드포인트 추출 오류 발생: {e}")
        return '', ''



# 새로운 함수 추가
def extract_cache_parameter_group_name(parameter_group):
    """Cache Parameter Group JSON에서 CacheParameterGroupName 값을 추출합니다."""
    try:
        if pd.isna(parameter_group) or not parameter_group.strip():
            return ''

        param_group = json.loads(parameter_group)
        return param_group.get('CacheParameterGroupName', '') if isinstance(param_group, dict) else ''
    except json.JSONDecodeError as e:
        print(f"JSON 디코딩 오류 발생: {e}")
        return ''
    except Exception as e:
        print(f"기타 오류 발생: {e}")
        return ''


def transform_elasticache_data(ec_csv, ecrep_csv):
    """ElastiCache 클러스터 데이터를 변환합니다."""
    # CSV 파일 읽기
    ec_data = pd.read_csv(ec_csv, encoding='utf-8')
    ecrep_data = pd.read_csv(ecrep_csv, encoding='utf-8')

    # 필요한 정보 병합을 위한 리스트 초기화
    merged_data = []

    for _, row in ecrep_data.iterrows():
        replication_group_id = row['Replication Group ID']
        ec_rows = ec_data[ec_data['Replication Group ID'] == replication_group_id]

        # ecrep의 데이터를 우선으로 사용하고, ec에서 추가 정보를 채워넣음
        cluster_names = ", ".join(ec_rows['Cache Cluster ID'].tolist()) if not ec_rows.empty else ''
        engines = ", ".join(ec_rows['Engine'].unique()) if not ec_rows.empty else ''
        vpc_ids = ", ".join(ec_rows['Cache Subnet Group Name'].unique()) if not ec_rows.empty else ''
        subnets = ", ".join(ec_rows['Cache Subnet Group Name'].unique()) if not ec_rows.empty else ''

        # Cache Parameter Group에서 CacheParameterGroupName 추출
        parameter_group_name = ec_rows['Cache Parameter Group'].apply(extract_cache_parameter_group_name).iloc[
            0] if not ec_rows.empty else ''

        security_groups = ec_rows['Security Groups'].apply(format_security_groups).iloc[0] if not ec_rows.empty else ''
        cluster_mode = 'enabled' if row['Cluster Enabled'] else 'disabled'
        multi_az = 'Y' if row['Multi Az'] == 'enabled' else 'N'
        shards = len(json.loads(row['Node Groups']))
        nodes = ec_rows['Num Cache Nodes'].sum() if not ec_rows.empty else shards
        primary_endpoint, reader_endpoint = extract_endpoints(row['Node Groups'])
        backup = f"{row['Snapshot Retention Limit']} days" if not pd.isna(row['Snapshot Retention Limit']) else '-'
        encryption_at_rest = row['At Rest Encryption Enabled']
        description = row['Description']
        region = row['Region']

        # 병합할 데이터 추가
        merged_data.append({
            'Region': region,
            'Cluster Name': cluster_names,
            'Engine': engines,
            'VPC ID': vpc_ids,
            'Subnet Group': subnets,
            'Subnet ID': '-',
            'Parameter Group': parameter_group_name,  # 수정된 부분
            'Security Group': security_groups,
            'Cluster Mode': cluster_mode,
            'Multi-AZ': multi_az,
            'Shard': shards,
            'Node': nodes,
            'Primary Endpoint': primary_endpoint,
            'Reader Endpoint': reader_endpoint,
            'Backup retention period': backup,
            'Encryption at rest': encryption_at_rest,
            'Description': description,
            'Compared with Last Month': '-'
        })

    # 데이터프레임 생성
    transformed_data = pd.DataFrame(merged_data)
    return transformed_data


def load_and_transform_elasticache_data(ec_csv, ecrep_csv):
    return transform_elasticache_data(ec_csv, ecrep_csv)
