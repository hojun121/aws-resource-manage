from datetime import datetime
import os
import pandas as pd
import openpyxl
from modules.autoscaling import load_and_transform_autoscaling_data
from modules.cloudfront import load_and_transform_cloudfront_data
from modules.docdb import load_and_transform_docdb_data
from modules.ec import load_and_transform_elasticache_data
from modules.ec2 import load_and_transform_ec2_data
from modules.elb import load_and_transform_elb_data
from modules.iamrole import load_and_transform_iam_role_data
from modules.iamuser import load_and_transform_iam_user_data
from modules.iamgroup import load_and_transform_iam_group_data
from modules.network_acls import load_and_transform_network_acls_data
from modules.s3 import load_and_transform_s3_data
from modules.security_groups import load_and_transform_security_groups_data
from modules.subnet import load_and_transform_subnet_data
from modules.tg import load_and_transform_target_group_data
from modules.tgw import load_and_transform_tgw_data
from modules.vpc import load_and_transform_vpc_data
from modules.rds import load_and_transform_rds_data

# 파일 디렉토리 설정
upload_folder = 'file/upload'  # 업로드 폴더 경로
# Get today's date in 'YYMMDD' format
today = datetime.today().strftime('%y%m%d')

# Path to the output Excel file
output_excel_path = os.path.join('file/download', f'_Inventory_{today}.xlsx')

# 다운로드 디렉토리가 없으면 생성
os.makedirs('file/download', exist_ok=True)

file_header_mapping = {
    'alb': 'Name,Arn,Type,Scheme,Canonical Hosted Zone ID,Vpc ID,Created Time,Customer Owned Ipv4 Pool,Dns Name,IP Address Type,State Code,State Reason,Availability Zones,Security Groups,Load Balancer Attributes,Tags Src,Tags,Title,Akas,Partition,Region,Account ID,Sp Connection Name,Sp Ctx,Ctx',
    'nlb': 'Name,Arn,Type,Scheme,Canonical Hosted Zone ID,Created Time,Customer Owned Ipv4 Pool,Dns Name,IP Address Type,State Code,State Reason,Vpc ID,Availability Zones,Security Groups,Load Balancer Attributes,Tags Src,Tags,Title,Akas,Partition,Region,Account ID,Sp Connection Name,Sp Ctx,Ctx',
    'autoscaling': 'Name,Autoscaling Group Arn,Status,Created Time,New Instances Protected From Scale In,Launch Configuration Name,Default Cooldown,Desired Capacity,Max Instance Lifetime,Max Size,Min Size,Health Check Grace Period,Health Check Type,Placement Group,Service Linked Role Arn,Vpc Zone Identifier,Launch Template Name,Launch Template ID,Launch Template Version,On Demand Allocation Strategy,On Demand Base Capacity,On Demand Percentage Above Base Capacity,Spot Allocation Strategy,Spot Instance Pools,Spot Max Price,Mixed Instances Policy Launch Template Name,Mixed Instances Policy Launch Template ID,Mixed Instances Policy Launch Template Version,Mixed Instances Policy Launch Template Overrides,Availability Zones,Load Balancer Names,Target Group Arns,Instances,Enabled Metrics,Policies,Termination Policies,Suspended Processes,Tags Src,Tags,Title,Akas,Partition,Region,Account ID,Sp Connection Name,Sp Ctx,Ctx',
    'cloudfront': 'ID,Arn,Status,Caller Reference,Comment,Default Root Object,Domain Name,Enabled,E Tag,Http Version,Is Ipv6 Enabled,In Progress Invalidation Batches,Last Modified Time,Price Class,Web Acl ID,Active Trusted Key Groups,Active Trusted Signers,Aliases,Alias Icp Recordals,Cache Behaviors,Custom Error Responses,Default Cache Behavior,Logging,Origins,Origin Groups,Restrictions,Tags Src,Viewer Certificate,Title,Tags,Akas,Partition,Region,Account ID,Sp Connection Name,Sp Ctx,Ctx',
    'docdbcluster': 'Db Cluster Identifier,Arn,Status,Cluster Create Time,Backup Retention Period,Clone Group ID,Db Cluster Parameter Group,Db Cluster Resource ID,Db Subnet Group,Deletion Protection,Earliest Restorable Time,Endpoint,Engine,Engine Version,Hosted Zone ID,Kms Key ID,Latest Restorable Time,Master User Name,Multi Az,Percent Progress,Port,Preferred Backup Window,Preferred Maintenance Window,Reader Endpoint,Replication Source Identifier,Storage Encrypted,Associated Roles,Availability Zones,Enabled Cloudwatch Logs Exports,Members,Read Replica Identifiers,Vpc Security Groups,Tags Src,Tags,Title,Akas,Partition,Region,Account ID,Sp Connection Name,Sp Ctx,Ctx',
    'docdbinstance': 'Db Instance Identifier,Db Instance Arn,Db Cluster Identifier,Db Instance Status,Db Instance Class,Dbi Resource ID,Availability Zone,Backup Retention Period,Ca Certificate Identifier,Copy Tags To Snapshot,Db Subnet Group Arn,Db Subnet Group Description,Db Subnet Group Name,Db Subnet Group Status,Endpoint Address,Endpoint Hosted Zone ID,Endpoint Port,Engine,Engine Version,Instance Create Time,Kms Key ID,Latest Restorable Time,Preferred Backup Window,Preferred Maintenance Window,Promotion Tier,Publicly Accessible,Storage Encrypted,Vpc ID,Enabled Cloudwatch Logs Exports,Pending Modified Values,Status Infos,Subnets,Vpc Security Groups,Tags Src,Tags,Title,Akas,Partition,Region,Account ID,Sp Connection Name,Sp Ctx,Ctx',
    'ec': 'Cache Cluster ID,Arn,Cache Node Type,Cache Cluster Status,At Rest Encryption Enabled,Auth Token Enabled,Auto Minor Version Upgrade,Cache Cluster Create Time,Cache Subnet Group Name,Client Download Landing Page,Engine,Engine Version,Num Cache Nodes,Preferred Availability Zone,Preferred Maintenance Window,Replication Group ID,Snapshot Retention Limit,Snapshot Window,Transit Encryption Enabled,Auth Token Last Modified Date,IP Discovery,Network Type,Preferred Outpost Arn,Replication Group Log Delivery Enabled,Transit Encryption Mode,Cache Parameter Group,Notification Configuration,Pending Modified Values,Security Groups,Configuration Endpoint,Cache Nodes,Cache Security Groups,Log Delivery Configurations,Tags Src,Title,Tags,Akas,Partition,Region,Account ID,Sp Connection Name,Sp Ctx,Ctx',
    'ec2': 'Instance ID,Arn,Instance Type,Instance State,Monitoring State,Disable Api Termination,Ami Launch Index,Architecture,Boot Mode,Capacity Reservation ID,Capacity Reservation Specification,Client Token,Cpu Options Core Count,Cpu Options Threads Per Core,Ebs Optimized,Ena Support,Hypervisor,Iam Instance Profile Arn,Iam Instance Profile ID,Image ID,Instance Initiated Shutdown Behavior,Instance Lifecycle,Kernel ID,Key Name,Launch Time,Outpost Arn,Placement Affinity,Placement Availability Zone,Placement Group ID,Placement Group Name,Placement Host ID,Placement Host Resource Group Arn,Placement Partition Number,Placement Tenancy,Platform,Platform Details,Private IP Address,Private Dns Name,Public Dns Name,Public IP Address,Ram Disk ID,Root Device Name,Root Device Type,Source Dest Check,Spot Instance Request ID,Sriov Net Support,State Code,State Transition Reason,State Transition Time,Subnet ID,Tpm Support,Usage Operation,Usage Operation Update Time,User Data,Virtualization Type,Vpc ID,Block Device Mappings,Elastic Gpu Associations,Elastic Inference Accelerator Associations,Enclave Options,Hibernation Options,Launch Template Data,Licenses,Maintenance Options,Metadata Options,Network Interfaces,Private Dns Name Options,Product Codes,Security Groups,Instance Status,Tags Src,Title,Tags,Akas,Partition,Region,Account ID,Sp Connection Name,Sp Ctx,Ctx',
    'ecrep': 'Replication Group ID,Arn,Description,At Rest Encryption Enabled,Kms Key ID,Auth Token Enabled,Auth Token Last Modified Date,Automatic Failover,Cache Node Type,Cluster Enabled,Multi Az,Snapshot Retention Limit,Snapshot Window,Snapshotting Cluster ID,Status,Transit Encryption Enabled,Configuration Endpoint,Global Replication Group Info,Member Clusters,Member Clusters Outpost Arns,Node Groups,Pending Modified Values,User Group Ids,Title,Akas,Partition,Region,Account ID,Sp Connection Name,Sp Ctx,Ctx',
    'iamgroup': 'Name,Group ID,Path,Arn,Create Date,Inline Policies,Inline Policies Std,Attached Policy Arns,Users,Title,Akas,Partition,Region,Account ID,Sp Connection Name,Sp Ctx,Ctx',
    'iamrole': 'Name,Arn,Role ID,Create Date,Description,Instance Profile Arns,Max Session Duration,Path,Permissions Boundary Arn,Permissions Boundary Type,Role Last Used Date,Role Last Used Region,Tags Src,Inline Policies,Inline Policies Std,Attached Policy Arns,Assume Role Policy,Assume Role Policy Std,Title,Tags,Akas,Partition,Region,Account ID,Sp Connection Name,Sp Ctx,Ctx',
    'iamuser': 'Name,User ID,Path,Arn,Create Date,Password Last Used,Permissions Boundary Arn,Permissions Boundary Type,Mfa Enabled,Login Profile,Mfa Devices,Groups,Inline Policies,Inline Policies Std,Attached Policy Arns,Tags Src,Tags,Title,Akas,Partition,Region,Account ID,Sp Connection Name,Sp Ctx,Ctx',
    'nacls': 'Network Acl ID,Arn,Is Default,Vpc ID,Owner ID,Associations,Entries,Tags Src,Tags,Title,Akas,Partition,Region,Account ID,Sp Connection Name,Sp Ctx,Ctx',
    'rt': 'Route Table ID,Vpc ID,Owner ID,Associations,Routes,Propagating Vgws,Tags Src,Tags,Title,Akas,Partition,Region,Account ID,Sp Connection Name,Sp Ctx,Ctx',
    's3': 'Name,Arn,Creation Date,Bucket Policy Is Public,Versioning Enabled,Versioning Mfa Delete,Block Public Acls,Block Public Policy,Ignore Public Acls,Restrict Public Buckets,Event Notification Configuration,Server Side Encryption Configuration,Acl,Lifecycle Rules,Logging,Object Lock Configuration,Object Ownership Controls,Policy,Policy Std,Replication,Website Configuration,Tags Src,Tags,Title,Akas,Region,Partition,Account ID,Sp Connection Name,Sp Ctx,Ctx',
    'sg': 'Group Name,Group ID,Arn,Description,Vpc ID,Owner ID,IP Permissions,IP Permissions Egress,Tags Src,Tags,Title,Akas,Partition,Region,Account ID,Sp Connection Name,Sp Ctx,Ctx',
    'sgrule': 'Security Group Rule ID,Group Name,Group ID,Is Egress,Type,Vpc ID,Owner ID,Group Owner ID,Description,IP Protocol,From Port,To Port,Cidr IP,Cidr Ipv4,Cidr Ipv6,Pair Group ID,Referenced Group ID,Pair Group Name,Pair Peering Status,Referenced Peering Status,Pair User ID,Referenced User ID,Pair Vpc ID,Referenced Vpc ID,Pair Vpc Peering Connection ID,Referenced Vpc Peering Connection ID,Prefix List ID,Title,Akas,Partition,Region,Account ID,Sp Connection Name,Sp Ctx,Ctx',
    'subnet': 'Subnet ID,Subnet Arn,Vpc ID,Cidr Block,State,Owner ID,Assign Ipv6 Address On Creation,Available IP Address Count,Availability Zone,Availability Zone ID,Customer Owned Ipv4 Pool,Default For Az,Map Customer Owned IP On Launch,Map Public IP On Launch,Outpost Arn,Ipv6 Cidr Block Association Set,Tags Src,Tags,Title,Akas,Partition,Region,Account ID,Sp Connection Name,Sp Ctx,Ctx',
    'tg': 'Target Group Name,Target Group Arn,Target Type,Load Balancer Arns,Port,Vpc ID,Protocol,Matcher Http Code,Matcher Grpc Code,Healthy Threshold Count,Unhealthy Threshold Count,Health Check Enabled,Health Check Interval Seconds,Health Check Path,Health Check Port,Health Check Protocol,Health Check Timeout Seconds,Target Health Descriptions,Tags Src,Title,Tags,Akas,Partition,Region,Account ID,Sp Connection Name,Sp Ctx,Ctx',
    'vpc': 'Vpc ID,Arn,Cidr Block,State,Is Default,Dhcp Options ID,Instance Tenancy,Owner ID,Cidr Block Association Set,Ipv6 Cidr Block Association Set,Tags Src,Title,Tags,Akas,Partition,Region,Account ID,Sp Connection Name,Sp Ctx,Ctx',
    'vpcigw': 'Internet Gateway ID,Owner ID,Attachments,Tags Src,Tags,Title,Akas,Partition,Region,Account ID,Sp Connection Name,Sp Ctx,Ctx',
    'tgw': 'Transit Gateway ID,Transit Gateway Arn,State,Owner ID,Description,Creation Time,Amazon Side Asn,Association Default Route Table ID,Auto Accept Shared Attachments,Default Route Table Association,Default Route Table Propagation,Dns Support,Multicast Support,Propagation Default Route Table ID,Vpn Ecmp Support,Cidr Blocks,Tags Src,Tags,Title,Akas,Partition,Region,Account ID,Sp Connection Name,Sp Ctx,Ctx',
    'rdscluster': 'Db Cluster Identifier,Arn,Status,Resource ID,Create Time,Activity Stream Kinesis Stream Name,Activity Stream Kms Key ID,Activity Stream Mode,Activity Stream Status,Allocated Storage,Auto Minor Version Upgrade,Backtrack Consumed Change Records,Backtrack Window,Backup Retention Period,Capacity,Character Set Name,Clone Group ID,Copy Tags To Snapshot,Cross Account Clone,Database Name,Db Cluster Parameter Group,Db Subnet Group,Deletion Protection,Earliest Backtrack Time,Earliest Restorable Time,Endpoint,Engine,Engine Mode,Engine Version,Global Write Forwarding Requested,Global Write Forwarding Status,Hosted Zone ID,Http Endpoint Enabled,Iam Database Authentication Enabled,Kms Key ID,Latest Restorable Time,Master User Name,Multi Az,Percent Progress,Port,Preferred Backup Window,Preferred Maintenance Window,Reader Endpoint,Storage Encrypted,Associated Roles,Availability Zones,Custom Endpoints,Members,Option Group Memberships,Domain Memberships,Enabled Cloudwatch Logs Exports,Pending Maintenance Actions,Read Replica Identifiers,Vpc Security Groups,Tags Src,Tags,Title,Akas,Partition,Region,Account ID,Sp Connection Name,Sp Ctx,Ctx',
    'rdsinstance': 'Db Instance Identifier,Arn,Db Cluster Identifier,Status,Class,Resource ID,Allocated Storage,Auto Minor Version Upgrade,Availability Zone,Backup Retention Period,Ca Certificate Identifier,Character Set Name,Copy Tags To Snapshot,Customer Owned IP Enabled,Port,Db Name,Db Subnet Group Arn,Db Subnet Group Description,Db Subnet Group Name,Db Subnet Group Status,Deletion Protection,Endpoint Address,Endpoint Hosted Zone ID,Endpoint Port,Engine,Engine Version,Enhanced Monitoring Resource Arn,Iam Database Authentication Enabled,Create Time,Iops,Kms Key ID,Latest Restorable Time,License Model,Master User Name,Max Allocated Storage,Monitoring Interval,Monitoring Role Arn,Multi Az,Nchar Character Set Name,Performance Insights Enabled,Performance Insights Kms Key ID,Performance Insights Retention Period,Preferred Backup Window,Preferred Maintenance Window,Promotion Tier,Publicly Accessible,Read Replica Source Db Instance Identifier,Replica Mode,Secondary Availability Zone,Storage Encrypted,Storage Throughput,Storage Type,Tde Credential Arn,Timezone,Vpc ID,Associated Roles,Certificate,Db Parameter Groups,Db Security Groups,Domain Memberships,Enabled Cloudwatch Logs Exports,Option Group Memberships,Pending Maintenance Actions,Processor Features,Read Replica Db Cluster Identifiers,Read Replica Db Instance Identifiers,Status Infos,Subnets,Vpc Security Groups,Tags Src,Tags,Title,Akas,Partition,Region,Account ID,Sp Connection Name,Sp Ctx,Ctx'
}


def identify_files(upload_folder):
    files_dict = {}

    for file_name in os.listdir(upload_folder):
        if file_name.endswith('.csv'):
            file_path = os.path.join(upload_folder, file_name)

            with open(file_path, 'r', encoding='utf-8') as file:
                first_line = file.readline().strip()

                for key, header in file_header_mapping.items():
                    if first_line == header:
                        if key in files_dict:
                            files_dict[key].append(file_path)
                        else:
                            files_dict[key] = [file_path]

                        break
    return files_dict

def adjust_column_widths(sheet):
    for column in sheet.columns:
        max_length = 0
        column_letter = column[0].column_letter # Get the column name
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        adjusted_width = (max_length + 2)  # Add some padding
        sheet.column_dimensions[column_letter].width = adjusted_width

def process_and_save_sheets():
    try:
        files_dict = identify_files(upload_folder)

        with pd.ExcelWriter(output_excel_path, engine='xlsxwriter') as writer:

            # VPC 모듈 처리
            if 'vpc' in files_dict and 'vpcigw' in files_dict:
                vpc_csv = files_dict['vpc'][0]  # 첫 번째 파일을 사용
                vpcigw_csv = files_dict['vpcigw'][0]  # 첫 번째 파일을 사용
                transformed_data = load_and_transform_vpc_data(vpc_csv, vpcigw_csv)
                if not transformed_data.empty:
                    transformed_data.to_excel(writer, sheet_name='VPC', index=False)

            # TGW (Transit Gateway) 모듈 처리
            if 'tgw' in files_dict:
                tgw_csv = files_dict['tgw'][0]  # 첫 번째 파일을 사용
                transformed_data = load_and_transform_tgw_data(tgw_csv)
                if not transformed_data.empty:
                    transformed_data.to_excel(writer, sheet_name='TGW', index=False)

            # Subnet 모듈 처리
            if 'subnet' in files_dict and 'rt' in files_dict and 'nacls' in files_dict:
                subnet_csv = files_dict['subnet'][0]  # 첫 번째 파일을 사용
                rt_csv = files_dict['rt'][0]  # 첫 번째 파일을 사용
                nacls_csv = files_dict['nacls'][0]  # 첫 번째 파일을 사용
                transformed_data = load_and_transform_subnet_data(subnet_csv, rt_csv, nacls_csv)
                if not transformed_data.empty:
                    transformed_data.to_excel(writer, sheet_name='Subnet', index=False)

            # Security Groups 모듈 처리
            if 'sg' in files_dict and 'sgrule' in files_dict:
                sg_csv = files_dict['sg'][0]  # 첫 번째 파일을 사용
                sgrule_csv = files_dict['sgrule'][0]  # 첫 번째 파일을 사용
                transformed_data = load_and_transform_security_groups_data(sg_csv, sgrule_csv)
                if not transformed_data.empty:
                    transformed_data.to_excel(writer, sheet_name='Security Groups', index=False)

            # Network ACLs 모듈 처리
            if 'nacls' in files_dict:
                network_acls_csv = files_dict['nacls'][0]  # 첫 번째 파일을 사용
                transformed_data = load_and_transform_network_acls_data(network_acls_csv)
                if not transformed_data.empty:
                    transformed_data.to_excel(writer, sheet_name='Network ACLs', index=False)

            # EC2 모듈 처리
            if 'ec2' in files_dict:
                ec2_csv = files_dict['ec2'][0]  # 첫 번째 파일을 사용
                transformed_data = load_and_transform_ec2_data(ec2_csv)
                if not transformed_data.empty:
                    transformed_data.to_excel(writer, sheet_name='EC2', index=False)

            # ELB 모듈 처리
            if 'alb' in files_dict or 'nlb' in files_dict:
                alb_csv = files_dict['alb'][0] if 'alb' in files_dict else None
                nlb_csv = files_dict['nlb'][0] if 'nlb' in files_dict else None

                # 존재하는 파일만 함수에 전달
                if alb_csv or nlb_csv:
                    transformed_data = load_and_transform_elb_data(alb_csv, nlb_csv)
                    if not transformed_data.empty:
                        transformed_data.to_excel(writer, sheet_name='ELB', index=False)

            # Target Group 모듈 처리
            if 'tg' in files_dict:
                tg_csv = files_dict['tg'][0]  # 첫 번째 파일을 사용
                transformed_data = load_and_transform_target_group_data(tg_csv)
                if not transformed_data.empty:
                    transformed_data.to_excel(writer, sheet_name='Target Group', index=False)

            # Autoscaling 모듈 처리
            if 'autoscaling' in files_dict:
                autoscaling_csv = files_dict['autoscaling'][0]  # 첫 번째 파일을 사용
                transformed_data = load_and_transform_autoscaling_data(autoscaling_csv)
                if not transformed_data.empty:
                    transformed_data.to_excel(writer, sheet_name='Auto Scaling', index=False)

            # EC 모듈 처리
            if 'ec' in files_dict and 'ecrep' in files_dict:
                ec_csv = files_dict['ec'][0]  # 첫 번째 파일을 사용
                ecrep_csv = files_dict['ecrep'][0]  # 첫 번째 파일을 사용
                transformed_data = load_and_transform_elasticache_data(ec_csv, ecrep_csv)
                if not transformed_data.empty:
                    transformed_data.to_excel(writer, sheet_name='ElastiCache', index=False)

            # CloudFront 모듈 처리
            if 'cloudfront' in files_dict:
                cloudfront_csv = files_dict['cloudfront'][0]  # 첫 번째 파일을 사용
                transformed_data = load_and_transform_cloudfront_data(cloudfront_csv)
                if not transformed_data.empty:
                    transformed_data.to_excel(writer, sheet_name='CloudFront', index=False)

            # S3 모듈 처리
            if 's3' in files_dict:
                s3_csv = files_dict['s3'][0]  # 첫 번째 파일을 사용
                transformed_data = load_and_transform_s3_data(s3_csv)
                if not transformed_data.empty:
                    transformed_data.to_excel(writer, sheet_name='S3', index=False)

            # IAM Group 모듈 처리
            if 'iamgroup' in files_dict:
                iamgroup_csv = files_dict['iamgroup'][0]  # 첫 번째 파일을 사용
                transformed_data = load_and_transform_iam_group_data(iamgroup_csv)
                if not transformed_data.empty:
                    transformed_data.to_excel(writer, sheet_name='IAM Group', index=False)

            # IAM Role 모듈 처리
            if 'iamrole' in files_dict:
                iamrole_csv = files_dict['iamrole'][0]  # 첫 번째 파일을 사용
                transformed_data = load_and_transform_iam_role_data(iamrole_csv)
                if not transformed_data.empty:
                    transformed_data.to_excel(writer, sheet_name='IAM Role', index=False)

            # IAM User 모듈 처리
            if 'iamuser' in files_dict:
                iamuser_csv = files_dict['iamuser'][0]  # 첫 번째 파일을 사용
                transformed_data = load_and_transform_iam_user_data(iamuser_csv)
                if not transformed_data.empty:
                    transformed_data.to_excel(writer, sheet_name='IAM User', index=False)

            # RDS 클러스터 및 인스턴스 처리
            if 'rdscluster' in files_dict and 'rdsinstance' in files_dict:
                rdscluster_csv = files_dict['rdscluster'][0]  # 첫 번째 파일을 사용
                rdsinstance_csv = files_dict['rdsinstance'][0]  # 첫 번째 파일을 사용
                transformed_data = load_and_transform_rds_data(rdscluster_csv, rdsinstance_csv)
                if not transformed_data.empty:
                    transformed_data.to_excel(writer, sheet_name='RDS', index=False)

            # DocDB 클러스터 및 인스턴스 처리
            if 'docdbcluster' in files_dict and 'docdbinstance' in files_dict:
                docdbcluster_csv = files_dict['docdbcluster'][0]  # 첫 번째 파일을 사용
                docdbinstance_csv = files_dict['docdbinstance'][0]  # 첫 번째 파일을 사용
                transformed_data = load_and_transform_docdb_data(docdbcluster_csv, docdbinstance_csv)
                if not transformed_data.empty:
                    transformed_data.to_excel(writer, sheet_name='DocDB', index=False)

        # Adjust column widths after saving the Excel file
        wb = openpyxl.load_workbook(output_excel_path)
        for sheet in wb.sheetnames:
            ws = wb[sheet]
            adjust_column_widths(ws)
        wb.save(output_excel_path)


    except Exception as e:
        print(f"An error occurred: {e}")
        if os.path.exists(output_excel_path):
            os.remove(output_excel_path)



# 시트 처리 및 저장
process_and_save_sheets()
