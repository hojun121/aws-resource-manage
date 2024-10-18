import pandas as pd
import json


def load_sg_rules_mapping(sgrule_data):
    """
    sgrule.csv 파일을 로드하여 Security Group ID와 Direction을 조합해 Rule ID를 매핑합니다.
    """
    try:
        sgrule_data['direction'] = sgrule_data['is_egress'].apply(lambda x: 'Outbound' if x else 'Inbound')
        sgrule_data['rule_key'] = sgrule_data['group_id'] + '-' + sgrule_data['direction']
        rule_mapping = dict(zip(sgrule_data['rule_key'], sgrule_data['security_group_rule_id']))
        return rule_mapping
    except Exception as e:
        print(f"Error loading sgrule dataframe: {e}")
        return {}


def get_rule_id(sg_id, direction, rule_mapping):
    """
    Security Group ID와 Direction으로 Rule ID를 찾아 반환합니다.
    """
    key = f"{sg_id}-{direction}"
    return rule_mapping.get(key, "-")


def get_name_from_tags(tags):
    """
    태그에서 Name을 가져옵니다. 없으면 '-' 반환.
    """
    try:
        return tags.get("Name", "-") if isinstance(tags, dict) else "-"
    except Exception as e:
        print(f"Tags parsing error: {e}")
        return "-"


def comments_from_rule(rule, protocol, source_dest, name, sg_name):
    comments = ""

    # All IPs are open check
    if source_dest == "0.0.0.0/0":
        comments += "All IPs are open"

    # All ports are open check
    if protocol == "All":
        if comments:
            comments += " and all ports are open\n"
        else:
            comments = "All ports are open\n"

    # Name이 하이픈이면 추가로 'No security group name' 추가
    if name == "-":
        comments += ", No security group name" if comments else "No security group name"

    # Default Security Group 여부 확인
    if sg_name.lower() == 'default':
        if comments:
            comments += " and Default Security Group has rules\n"
        else:
            comments = "Default Security Group has rules\n"

    return comments.rstrip('\n')


def process_rule(rule, direction, sg_name, sg_id, region, rule_mapping, tags):
    """
    보안 그룹의 규칙을 파싱하고 지정된 형식으로 변환합니다.
    """
    rules_list = []
    name = get_name_from_tags(tags)

    for r in rule:
        protocol = "All" if r.get("IpProtocol") == "-1" else r.get("IpProtocol", "-")  # Protocol이 -1이면 All로 표기

        # 포트 범위 설정 (None이면 '-'로 처리)
        from_port = r.get('FromPort', '-')
        to_port = r.get('ToPort', '-')
        from_port = '-' if from_port is None else from_port
        to_port = '-' if to_port is None else to_port
        port_range = f"{from_port}" if from_port == to_port else f"{from_port}-{to_port}"

        # CIDR, IPv6 주소 범위 설정
        cidr_blocks = [ip_range.get("CidrIp", "-") for ip_range in r.get("IpRanges", [])]
        ipv6_blocks = [ip_range.get("CidrIpv6", "-") for ip_range in r.get("Ipv6Ranges", [])]
        source_dest = ', '.join(cidr_blocks + ipv6_blocks) if cidr_blocks + ipv6_blocks else "-"

        # Rule ID 얻기
        rule_id = get_rule_id(sg_id, direction, rule_mapping)
        descriptions = [ip_range.get("Description", "-") for ip_range in r.get("IpRanges", [])]
        description = ', '.join(desc if desc else "-" for desc in descriptions)

        comments = comments_from_rule(r, protocol, source_dest, name, sg_name)

        rules_list.append({
            'Name': name,
            'Security Group Name': sg_name,
            'Group ID': sg_id,
            'Rule ID': rule_id,
            'Region': region,
            'Protocol': protocol,
            'Port Range': port_range,
            'Source/Destination': source_dest,
            'Direction': direction,
            'Description': description,
            'Comments': comments,
        })

    return rules_list


def transform_security_groups_data(sg_data, sgrule_data):
    """
    보안 그룹 데이터를 변환하여 Security Group의 규칙을 파싱합니다.
    """
    # Rule ID 매핑 데이터 로드
    rule_mapping = load_sg_rules_mapping(sgrule_data)

    # 변환된 데이터 리스트
    data_list = []

    for _, row in sg_data.iterrows():
        # Ingress Rules 처리
        ingress_rules = row['ip_permissions']
        data_list.extend(
            process_rule(ingress_rules, 'Inbound', row['group_name'], row['group_id'], row['region'], rule_mapping,
                         row['tags']))

        # Egress Rules 처리
        egress_rules = row['ip_permissions_egress']
        data_list.extend(
            process_rule(egress_rules, 'Outbound', row['group_name'], row['group_id'], row['region'], rule_mapping,
                         row['tags']))

    # 데이터 프레임 생성
    transformed_data = pd.DataFrame(data_list)

    # Sort Security Group by Name in Desc
    transformed_data = transformed_data.sort_values(by='Name', ascending=False)

    return transformed_data


def load_and_transform_security_groups_data(sg_data, sgrule_data):
    return transform_security_groups_data(sg_data, sgrule_data)
