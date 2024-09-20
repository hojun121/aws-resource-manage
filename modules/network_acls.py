import pandas as pd
import json


def parse_json_field(field):
    """ JSON 문자열을 Python 객체로 변환 """
    if isinstance(field, str):
        try:
            return json.loads(field.replace("'", '"'))
        except json.JSONDecodeError as e:
            print(f"JSON 디코딩 오류 발생: {e}")
            return []
        except Exception as e:
            print(f"기타 오류 발생: {e}")
            return []

def process_acl_entries(entries, nacl_name, nacl_id, vpc_id, region):
    """ ACL 엔트리 리스트를 처리하여 적절한 형식으로 변환 """
    processed_entries = []
    for entry in entries:
        protocol = entry.get("Protocol", "All")
        if protocol == "-1":
            protocol = "All"
        elif protocol == "6":
            protocol = "TCP (6)"

        port_range = entry.get("PortRange", {})
        if port_range:
            from_port = port_range.get("From", "All")
            to_port = port_range.get("To", "All")
            if from_port == 0 and to_port == 65535:
                port_range_str = "All"
            elif from_port == to_port:
                port_range_str = str(from_port)
            else:
                port_range_str = f"{from_port}-{to_port}"
        else:
            port_range_str = "All"

        rule_number = entry.get("RuleNumber", "*")
        if rule_number == 32767:
            rule_number = "*"

        action = entry.get("RuleAction", "Deny").capitalize()
        source = entry.get("CidrBlock", "0.0.0.0/0") or entry.get("Ipv6CidrBlock", "0.0.0.0/0")

        processed_entries.append({
            'Region': region,
            'NACL Name': nacl_name,
            'NACL ID': nacl_id,
            'VPC': vpc_id,
            'Direction': "Inbound" if not entry.get("Egress") else "Outbound",
            'Rule#': rule_number,
            'Type': 'All traffic' if protocol == "All" else 'Custom traffic',
            'Protocol': protocol,
            'Port Range': port_range_str,
            'Source': source,
            'Allow / Deny': action,
            'Description': '-',
            'Compared with Last Month': '-'
        })
    return processed_entries

def transform_nacls_data(nacls_csv_file):
    """ CSV 파일을 읽어 변환된 데이터를 반환 """
    nacls_df = pd.read_csv(nacls_csv_file, encoding='utf-8')

    # 변환된 데이터 리스트
    data_list = []

    for _, row in nacls_df.iterrows():
        entries = parse_json_field(row['Entries'])

        nacl_name = row['Title']
        if nacl_name == row['Network Acl ID']:
            nacl_name = '-'

        data_list.extend(
            process_acl_entries(entries, nacl_name, row['Network Acl ID'], row['Vpc ID'], row['Region']))

    # 데이터 프레임 생성
    transformed_data = pd.DataFrame(data_list)
    transformed_data = transformed_data.sort_values(by='NACL Name', ascending=False)

    return transformed_data

def load_and_transform_network_acls_data(nacls_csv_file):
    return transform_nacls_data(nacls_csv_file)
