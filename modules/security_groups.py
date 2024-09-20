import pandas as pd
import json


def parse_json_field(field):
    """
    JSON 형태의 필드를 파싱하여 리스트로 반환합니다.
    """
    try:
        return json.loads(field.replace("'", '"'))
    except json.JSONDecodeError as e:
        print(f"JSON 디코딩 오류 발생: {e}")
        return []
    except Exception as e:
        print(f"기타 오류 발생: {e}")
        return []


def load_sg_rules_mapping(sgrule_csv_file):
    """
    sgrule.csv 파일을 로드하여 Security Group ID와 Direction을 조합해 Rule ID를 매핑합니다.
    """
    try:
        sgrule_df = pd.read_csv(sgrule_csv_file, encoding='utf-8')
        # Ingress와 Egress를 구분하여 Rule Key 생성
        sgrule_df['Direction'] = sgrule_df['Is Egress'].apply(lambda x: 'Outbound' if x else 'Inbound')
        sgrule_df['Rule Key'] = sgrule_df['Group ID'] + '-' + sgrule_df['Direction']
        rule_mapping = dict(zip(sgrule_df['Rule Key'], sgrule_df['Security Group Rule ID']))
        return rule_mapping
    except Exception as e:
        print(f"Error loading sgrule.csv: {e}")
        return {}


def get_rule_id(sg_id, direction, rule_mapping):
    """
    Security Group ID와 Direction으로 Rule ID를 찾아 반환합니다.
    """
    key = f"{sg_id}-{direction}"
    return rule_mapping.get(key, "-")


def get_name_from_tags(tags):
    """
    Tries to extract the 'Name' field from the given tags string.
    If 'Name' is not found or if there is any error (e.g., non-string data),
    it returns a default value of '-'.
    """
    if not isinstance(tags, str):
        # If the tags value is not a string, return '-'
        return "-"

    try:
        # Attempt to parse the tags as JSON
        tags_dict = json.loads(tags.replace("'", '"'))
        # Check if the parsed value is a dictionary and return the 'Name' field, or '-'
        return tags_dict.get("Name", "-") if isinstance(tags_dict, dict) else "-"
    except Exception as e:
        # Handle parsing errors by printing the error and returning '-'
        print(f"Tags parsing error: {e}")
        return "-"


def process_rule(rule, direction, sg_name, sg_id, region, rule_mapping, tags):
    """
    보안 그룹의 규칙을 파싱하고 지정된 형식으로 변환합니다.
    """
    rules_list = []
    name = get_name_from_tags(tags)  # Name 값을 Tags에서 가져옴

    for r in rule:
        protocol = "All" if r.get("IpProtocol") == "-1" else r.get("IpProtocol", "-")  # Protocol이 -1이면 All로 표기

        # None이면 '-'로 치환하여 포트 범위를 설정
        from_port = r.get('FromPort', '-')
        to_port = r.get('ToPort', '-')
        from_port = '-' if from_port is None else from_port
        to_port = '-' if to_port is None else to_port
        port_range = f"{from_port}" if from_port == to_port else f"{from_port}-{to_port}"  # Port Range 변환

        cidr_blocks = [ip_range.get("CidrIp", "-") for ip_range in r.get("IpRanges", [])]
        ipv6_blocks = [ip_range.get("CidrIpv6", "-") for ip_range in r.get("Ipv6Ranges", [])]
        source_dest = ', '.join(cidr_blocks + ipv6_blocks) if cidr_blocks + ipv6_blocks else "-"

        rule_id = get_rule_id(sg_id, direction, rule_mapping)
        descriptions = [ip_range.get("Description", "-") for ip_range in r.get("IpRanges", [])]

        # Description이 없는 경우 Default 처리
        description = ', '.join(desc if desc else "-" for desc in descriptions)

        # Check Result 결정
        check_result = ""
        if source_dest == "0.0.0.0/0":
            check_result += "All IPs are open"
        if protocol == "All":
            if check_result:
                check_result += " and all ports are open\n"
            else:
                check_result = "All ports are open\n"

        if sg_name.lower() == 'default' and check_result:
            check_result += "Default Security Group has rules\n"
        elif sg_name.lower() == 'default':
            check_result = "Default Security Group has rules\n"

        # 마지막에 \n이 있을 경우 제거
        check_result = check_result.rstrip('\n')

        rules_list.append({
            'Region': region,
            'Name': name,
            'Security Group Name': sg_name,
            'Group ID': sg_id,
            'Rule ID': rule_id,
            'Protocol': protocol,
            'Port Range': port_range,
            'Source/Destination': source_dest,
            'Direction': direction,
            'Description': description,
            'Check Result': check_result,
            'Compared with Last Month': '-'
        })
    return rules_list


def transform_security_groups_data(security_groups_csv_file, sgrule_csv_file):
    """
    보안 그룹 데이터 파일을 변환하여 DataFrame 형태로 반환합니다.
    """
    sg_df = pd.read_csv(security_groups_csv_file, encoding='utf-8')

    # Rule ID 매핑 데이터 로드
    rule_mapping = load_sg_rules_mapping(sgrule_csv_file)

    # 변환된 데이터 리스트
    data_list = []

    for _, row in sg_df.iterrows():
        # Ingress Rules 처리
        ingress_rules = parse_json_field(row['IP Permissions'])
        data_list.extend(
            process_rule(ingress_rules, 'Inbound', row['Group Name'], row['Group ID'], row['Region'], rule_mapping, row['Tags']))

        # Egress Rules 처리
        egress_rules = parse_json_field(row['IP Permissions Egress'])
        data_list.extend(
            process_rule(egress_rules, 'Outbound', row['Group Name'], row['Group ID'], row['Region'], rule_mapping, row['Tags']))

    # 데이터 프레임 생성
    transformed_data = pd.DataFrame(data_list)

    # Sort Security Group by Name in Desc
    transformed_data = transformed_data.sort_values(by='Name', ascending=False)

    return transformed_data


def load_and_transform_security_groups_data(security_groups_csv_file, sgrule_csv_file):
    return transform_security_groups_data(security_groups_csv_file, sgrule_csv_file)
