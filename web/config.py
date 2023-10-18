# with open('/usr/src/app/data/restor.ini', 'r', encoding='UTF-8') as file:
# with open('/home/flask/services/script/data/restor.ini', 'r', encoding='UTF-8') as file:
# with open('/web/data/restor.ini', 'r', encoding='UTF-8') as file:
# with open('/home/adminer/thinclient_drives/D:/OTS/Dev/Project/1C_DB_RESTORE/data/restor.ini', 'r', encoding='UTF-8') as file:
# with open('/home/project/BD_RECOVERY/data/restor.ini', 'r', encoding='UTF-8') as file:
# import datetime

docker_path = '/usr/src/app/'
with open(f'{docker_path}data/restor.ini', 'r', encoding='UTF-8') as file:
    conf_dict = dict()
    for ins in file.read().split('\n'):
        if '==' in ins:
            conf_dict[ins.split('==')[0].strip()] = ins.split('==')[1].strip()

ldsp_server = conf_dict['ldsp_server']

root_dn = conf_dict['root_dn']

d_name = conf_dict['d_name']

sw_password = conf_dict['sw_password']

sw_username = conf_dict['sw_username']

db_type = conf_dict['db_type']

db_ip = conf_dict['db_ip']

db_inst = conf_dict['db_inst']

db_pass = conf_dict['db_pass']

db_user = conf_dict['db_user']

db_port = conf_dict['db_port']

db_db = conf_dict['db_db']

adm_group = conf_dict['adm_group']

tab_name = conf_dict['tab_name']

odbc = 'ODBC Driver 17 for SQL Server'

port_smb = 139

prefix = 'Recovery_'

arh_dict = {
    'BU1': {'smb_path': '', 'smb_server': 'rpz-srv-arhive', 'smb_name': 'Storage3', 'db_ip': '173.34.9.105',
            'arh_ip': '173.34.7.8', 'arh_name': 'BU1',
            'sql_inst': '173.34.9.105\\SQL1'},
    'BUR': {'smb_path': '', 'smb_server': 'rpz-srv-arhive', 'smb_name': 'Storage3', 'db_ip': '173.34.9.105',
            'arh_ip': '173.34.7.8', 'arh_name': 'BU1',
            'sql_inst': '173.34.9.105\\SQL1'},
    'ZUP3': {'smb_path': '', 'smb_server': 'rpz-srv-arhive', 'smb_name': 'Storage3', 'db_ip': '173.34.9.105',
             'arh_ip': '173.34.7.8', 'arh_name': 'ZUP3',
             'sql_inst': '173.34.9.105\\SQL1'},
    'DOC': {'smb_path': '', 'smb_server': 'rpz-srv-arhive', 'smb_name': 'Storage3', 'db_ip': '173.34.9.105',
            'arh_ip': '173.34.7.8', 'arh_name': 'doc_rpz_corp',
            'sql_inst': '173.34.9.105\\SQL1'},

    'doc': {'smb_path': '', 'smb_server': 'rpz-srv-arhive', 'smb_name': 'Storage3', 'db_ip': '173.34.9.105',
            'arh_ip': '173.34.7.8', 'arh_name': 'doc_rpz_corp',
            'sql_inst': '173.34.9.105\\SQL1'},

    'ZUP': {'smb_path': '', 'smb_server': 'rpz-srv-arhive', 'smb_name': 'Storage3', 'db_ip': '173.34.9.105',
             'arh_ip': '173.34.7.8', 'arh_name': 'ZUP3',
             'sql_inst': '173.34.9.105\\SQL1'},

    'AdventureWorks2014': {'smb_path': '', 'smb_server': 'rpz-srv-arhive', 'smb_name': 'Storage3',
                           'db_ip': 'rpz-srv-arhive', 'db_ip1': '173.34.9.105',
                           'arh_ip': '173.34.7.8', 'arh_name': 'AdventureWorks2014', 'sql_inst': '173.34.9.105\\SQL1'},
    'SLRPZ': {'smb_path': '/Storage3', 'smb_server': 'srv-arhpolk', 'smb_name': 'backup', 'db_ip': '173.34.9.63',
              'arh_ip': '173.34.230.95', 'arh_name': 'rpz_erp', 'sql_inst': '173.34.9.63'},
    'AdventureWorks2008R2': {'smb_path': '/Storage3', 'smb_server': 'srv-arhpolk', 'smb_name': 'backup',
                             'db_ip': '173.34.9.63', 'arh_ip': '173.34.230.95',
                             'arh_name': 'AdventureWorks2008R2', 'sql_inst': '173.34.9.63'}
}


file_log_path = f"/{docker_path}log/"


