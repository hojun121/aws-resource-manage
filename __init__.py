import sys
from datetime import datetime
import os
import pandas as pd
import openpyxl
from openpyxl.styles import Alignment, PatternFill, Font, Border, Side
from sqlalchemy import create_engine

from modules.vpc import load_and_transform_vpc_data
from modules.tgw import load_and_transform_tgw_data
from modules.vep import load_and_transform_vep_data
from modules.pc import load_and_transform_pc_data
from modules.subnet import load_and_transform_subnet_data
from modules.security_groups import load_and_transform_security_groups_data
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
from modules.tg import load_and_transform_target_group_data
from modules.rds import load_and_transform_rds_data

# PostgreSQL 연결 설정
DB_URI = 'postgresql://steampipe:ebf2_4830_b346@localhost:9193/steampipe'
try:
    engine = create_engine(DB_URI)
    connection = engine.connect()
    print("Connection successful.")

except Exception as e:
    print(f"Error occurred: {e}")
    sys.exit(1)

# 파일 디렉토리 설정
upload_folder = 'file/upload'  # 업로드 폴더 경로
today = datetime.today().strftime('%y%m%d')
os.makedirs('file/download', exist_ok=True)

schema = "dmpro_prod"  # 여기서 schema 이름을 지정

# Path to the output Excel file
output_excel_path = os.path.join('file/download', f'{schema}_inventory_{today}.xlsx')

queries = {
    'vpc': f'SELECT * FROM {schema}.aws_vpc',
    'igw': f'SELECT * FROM {schema}.aws_vpc_internet_gateway',
    'ngw': f'SELECT * FROM {schema}.aws_vpc_nat_gateway',
    'pc': f'SELECT * FROM {schema}.aws_vpc_peering_connection',
    'vep': f'SELECT * FROM {schema}.aws_vpc_endpoint',
    'tgw': f'SELECT * FROM {schema}.aws_ec2_transit_gateway',
    'subnet': f'SELECT * FROM {schema}.aws_vpc_subnet',
    'rt': f'SELECT * FROM {schema}.aws_vpc_route_table',
    'sg': f'SELECT * FROM {schema}.aws_vpc_security_group',
    'sgrule': f'SELECT * FROM {schema}.aws_vpc_security_group_rule',
    'nacls': f'SELECT * FROM {schema}.aws_vpc_network_acl',
    'ec2': f'SELECT * FROM {schema}.aws_ec2_instance',
    'ebs': f'SELECT * FROM {schema}.aws_ebs_volume',
    'alb': f'SELECT * FROM {schema}.aws_ec2_classic_load_balancer',
    'nlb': f'SELECT * FROM {schema}.aws_ec2_network_load_balancer',
    'tg': f'SELECT * FROM {schema}.aws_ec2_target_group',
    'autoscaling': f'SELECT * FROM {schema}.aws_ec2_autoscaling_group',
    'ec': f'SELECT * FROM {schema}.aws_elasticache_cluster',
    'cloudfront': f'SELECT * FROM {schema}.aws_cloudfront_cache_policy',
    's3': f'SELECT * FROM {schema}.aws_s3_bucket',
    'iamgroup': f'SELECT * FROM {schema}.aws_iam_group',
    'iamrole': f'SELECT * FROM {schema}.aws_iam_role',
    'iamuser': f'SELECT * FROM {schema}.aws_iam_access_key',
    'rdscluster': f'SELECT * FROM {schema}.aws_rds_db_cluster',
    'rdsinstance': f'SELECT * FROM {schema}.aws_rds_db_instance',
    'docdbcluster': f'SELECT * FROM {schema}.aws_docdb_cluster_instance',
    'docdbinstance': f'SELECT * FROM {schema}.aws_docdb_cluster_instance'
}


def process_and_save_sheets():
    try:
        with pd.ExcelWriter(output_excel_path, engine='xlsxwriter') as writer:
            # VPC 모듈 처리
            vpc_data = pd.read_sql(queries['vpc'], engine)
            igw_data = pd.read_sql(queries['igw'], engine)
            ngw_data = pd.read_sql(queries['ngw'], engine)
            if not vpc_data.empty:
                transformed_data = load_and_transform_vpc_data(vpc_data, igw_data, ngw_data)
                transformed_data.to_excel(writer, sheet_name='VPC', index=False)

            # VPC Endpoint 모듈 처리
            vep_data = pd.read_sql(queries['vep'], engine)
            if not vep_data.empty:
                transformed_data = load_and_transform_vep_data(vep_data)
                transformed_data.to_excel(writer, sheet_name='VPC Endpoint', index=False)

            # Peering Connection 모듈 처리
            pc_data = pd.read_sql(queries['pc'], engine)
            if not pc_data.empty:
                transformed_data = load_and_transform_pc_data(pc_data)
                transformed_data.to_excel(writer, sheet_name='Peering Connection', index=False)

            # TGW (Transit Gateway) 모듈 처리
            tgw_data = pd.read_sql(queries['tgw'], engine)
            if not tgw_data.empty:
                transformed_data = load_and_transform_tgw_data(tgw_data)
                transformed_data.to_excel(writer, sheet_name='Transit Gateway', index=False)

            # Subnet 모듈 처리
            subnet_data = pd.read_sql(queries['subnet'], engine)
            rt_data = pd.read_sql(queries['rt'], engine)
            network_acl_data = pd.read_sql(queries['nacls'], engine)
            if not subnet_data.empty:
                transformed_data = load_and_transform_subnet_data(subnet_data, rt_data, network_acl_data)
                transformed_data.to_excel(writer, sheet_name='Subnet', index=False)

            # Security Groups 모듈 처리
            sg_data = pd.read_sql(queries['sg'], engine)
            sgrule_data = pd.read_sql(queries['sgrule'], engine)
            if not sg_data.empty:
                transformed_data = load_and_transform_security_groups_data(sg_data, sgrule_data)
                transformed_data.to_excel(writer, sheet_name='Security Groups', index=False)

            # Network ACLs 모듈 처리
            network_acls_data = pd.read_sql(queries['nacls'], engine)
            if not network_acls_data.empty:
                transformed_data = load_and_transform_network_acls_data(network_acls_data)
                transformed_data.to_excel(writer, sheet_name='Network ACLs', index=False)

            # EC2 모듈 처리
            ec2_data = pd.read_sql(queries['ec2'], engine)
            ebs_data = pd.read_sql(queries['ebs'], engine)
            if not ec2_data.empty:
                transformed_data = load_and_transform_ec2_data(ec2_data, ebs_data)
                transformed_data.to_excel(writer, sheet_name='EC2', index=False)

            # # ELB 모듈 처리
            # alb_data = pd.read_sql(queries['alb'], engine)
            # nlb_data = pd.read_sql(queries['nlb'], engine)
            # if not alb_data.empty or not nlb_data.empty:
            #     transformed_data = load_and_transform_elb_data(alb_data, nlb_data)
            #     transformed_data.to_excel(writer, sheet_name='ELB', index=False)
            #
            # # Target Group 모듈 처리
            # tg_data = pd.read_sql(queries['tg'], engine)
            # if not tg_data.empty:
            #     transformed_data = load_and_transform_target_group_data(tg_data)
            #     transformed_data.to_excel(writer, sheet_name='Target Group', index=False)
            #
            # # Autoscaling 모듈 처리
            # autoscaling_data = pd.read_sql(queries['autoscaling'], engine)
            # if not autoscaling_data.empty:
            #     transformed_data = load_and_transform_autoscaling_data(autoscaling_data)
            #     transformed_data.to_excel(writer, sheet_name='Auto Scaling', index=False)
            #
            # # Elasticache 모듈 처리
            # ec_data = pd.read_sql(queries['ec'], engine)
            # if not ec_data.empty:
            #     transformed_data = load_and_transform_elasticache_data(ec_data)
            #     transformed_data.to_excel(writer, sheet_name='ElastiCache', index=False)
            #
            # # CloudFront 모듈 처리
            # cloudfront_data = pd.read_sql(queries['cloudfront'], engine)
            # if not cloudfront_data.empty:
            #     transformed_data = load_and_transform_cloudfront_data(cloudfront_data)
            #     transformed_data.to_excel(writer, sheet_name='CloudFront', index=False)
            #
            # # S3 모듈 처리
            # s3_data = pd.read_sql(queries['s3'], engine)
            # if not s3_data.empty:
            #     transformed_data = load_and_transform_s3_data(s3_data)
            #     transformed_data.to_excel(writer, sheet_name='S3', index=False)
            #
            # # IAM Group 모듈 처리
            # iamgroup_data = pd.read_sql(queries['iamgroup'], engine)
            # if not iamgroup_data.empty:
            #     transformed_data = load_and_transform_iam_group_data(iamgroup_data)
            #     transformed_data.to_excel(writer, sheet_name='IAM Group', index=False)
            #
            # # IAM Role 모듈 처리
            # iamrole_data = pd.read_sql(queries['iamrole'], engine)
            # if not iamrole_data.empty:
            #     transformed_data = load_and_transform_iam_role_data(iamrole_data)
            #     transformed_data.to_excel(writer, sheet_name='IAM Role', index=False)
            #
            # # IAM User 모듈 처리
            # iamuser_data = pd.read_sql(queries['iamuser'], engine)
            # if not iamuser_data.empty:
            #     transformed_data = load_and_transform_iam_user_data(iamuser_data)
            #     transformed_data.to_excel(writer, sheet_name='IAM User', index=False)
            #
            # # RDS 클러스터 및 인스턴스 처리
            # rdscluster_data = pd.read_sql(queries['rdscluster'], engine)
            # rdsinstance_data = pd.read_sql(queries['rdsinstance'], engine)
            # if not rdscluster_data.empty and not rdsinstance_data.empty:
            #     transformed_data = load_and_transform_rds_data(rdscluster_data, rdsinstance_data)
            #     transformed_data.to_excel(writer, sheet_name='RDS', index=False)
            #
            # # DocumentDB 클러스터 및 인스턴스 처리
            # docdbcluster_data = pd.read_sql(queries['docdbcluster'], engine)
            # docdbinstance_data = pd.read_sql(queries['docdbinstance'], engine)
            # if not docdbcluster_data.empty and not docdbinstance_data.empty:
            #     transformed_data = load_and_transform_docdb_data(docdbcluster_data, docdbinstance_data)
            #     transformed_data.to_excel(writer, sheet_name='DocumentDB', index=False)

        wb = openpyxl.load_workbook(output_excel_path)
        for sheet in wb.sheetnames:
            ws = wb[sheet]
            adjust_column_widths(ws)
            style_header(ws)
            center_align_cells(ws)
            apply_borders(ws)
        wb.save(output_excel_path)

    except Exception as e:
        print(f"Error occurred: {e}")

def adjust_column_widths(sheet):
    for column in sheet.columns:
        max_length = 0
        column_name = column[0].value
        for cell in column:
            try:
                if cell.value is not None:
                    max_length = max(max_length, len(str(cell.value)))
            except:
                pass
        if column_name == 'Tags':
            adjusted_width = 50
        else:
            adjusted_width = max_length + 2
        sheet.column_dimensions[column[0].column_letter].width = adjusted_width

def style_header(sheet):
    header_fill = PatternFill(start_color="334d1d", end_color="334d1d", fill_type="solid")
    header_font = Font(color="FFFFFF")

    for cell in sheet[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(vertical='center')

def apply_borders(sheet):
    thin_border = Border(left=Side(style='thin'), right=Side(style='thin'),
                         top=Side(style='thin'), bottom=Side(style='thin'))

    for row in sheet.iter_rows():
        for cell in row:
            cell.border = thin_border


def center_align_cells(sheet):
    for col_idx, col in enumerate(sheet.iter_cols(min_row=1, max_row=1), start=1):
        if col[0].value == "Tags":
            for row in sheet.iter_rows(min_col=col_idx, max_col=col_idx, min_row=2, max_row=sheet.max_row):
                for cell in row:
                    cell.alignment = Alignment(horizontal='right', vertical='center')
        else:
            for row in sheet.iter_rows(min_col=col_idx, max_col=col_idx, min_row=2, max_row=sheet.max_row):
                for cell in row:
                    cell.alignment = Alignment(vertical='center')


if __name__ == '__main__':
    process_and_save_sheets()
    print(f"Excel file saved at {output_excel_path}")
