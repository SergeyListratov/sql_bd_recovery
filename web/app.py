from flask import Flask, render_template, request, session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators
from ldap3 import Server, Connection, ALL, SUBTREE
import pyodbc
import config
from smb.SMBConnection import SMBConnection
import datetime
import os

app = Flask(__name__, template_folder=f'{config.docker_path}views')

app.secret_key = os.urandom(24).hex()

app.config['SECKRET KEY'] = '285bae97755f7aa5538deb0b4e2b162d4f5d3333bd59bcb6'

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


class LoginValidation(FlaskForm):
    user_name_pid = StringField('', [validators.InputRequired()],
                                render_kw={'autofocus': True, 'placeholder': 'Enter User'})

    user_pid_Password = PasswordField('', [validators.InputRequired()],
                                      render_kw={'autofocus': True, 'placeholder': 'Enter your login Password'})


def log_db_recovery(string):
    d = datetime.datetime.now().replace(microsecond=0)
    f = f"{config.file_log_path}{d.strftime('%d_%m_%Y_%H_%M_%S')}.log"
    with open(f, 'w', encoding='UTF-8') as file:
        file.write(string)


def get_ldap_authentication(user_name, user_pwd):
    ldap_user_name = user_name.strip()
    ldap_user_pwd = user_pwd.strip()
    ldsp_server = config.ldsp_server
    server = Server(ldsp_server, get_info=ALL)
    connection = Connection(server,
                            user=f'{ldap_user_name}{config.d_name}',
                            password=ldap_user_pwd)
    if not connection.bind():
        return None
    else:
        return connection


def ldap_filter(connection, user_name):
    root_d = config.root_dn
    search_filter = f"(sAMAccountName={user_name})"
    search_attribute = ['memberOf']
    connection.search(search_base=root_d,
                      search_scope=SUBTREE,
                      search_filter=search_filter,
                      attributes=search_attribute)
    db_list = [j.split(',')[0][20:] for j in filter(lambda i: i.startswith('CN=RestoreDB_'),
                                                    connection.response[0]['attributes']['memberOf'])]

    return db_list


def get_nic_name_tuple(db_name):
    for i in config.arh_dict:
        if i in db_name:
            return i, db_name


def get_mssql_conn(nic: str):
    sql_conn = None
    sql_conn_str = f'DRIVER={config.odbc};SERVER={config.arh_dict[nic]["sql_inst"]};' \
                   f'DATABASE={config.db_db};ENCRYPT=no;UID={config.db_user};' \
                   f'PWD={config.db_pass}'
    nn = 0
    while nn != 3:
        nn += 1
        try:
            sql_conn = pyodbc.connect(sql_conn_str)
            return sql_conn
        except pyodbc.DatabaseError as e:
            print(f' Attempt connection {nn}, error: ', e)
            break

    return sql_conn


def get_smb_conn(nic):
    smb_conn = SMBConnection(config.sw_username, config.sw_password, config.arh_dict[nic]['smb_server'],
                             domain=config.d_name[1:], use_ntlm_v2=True,
                             remote_name=f'{config.arh_dict[nic]["smb_server"]}')
    smb_conn.connect(config.arh_dict[nic]['arh_ip'], port=config.port_smb)

    return smb_conn


def get_data_from_mssql(sql_conn, sql_str):
    with sql_conn.cursor() as curs:
        curs.execute(sql_str)
        data = curs.fetchall()

    return data


def start_mssql_sp_start_job(sql_conn, db_name):
    try:
        sql_conn.execute(f"EXEC msdb.dbo.sp_start_job N'Recovery_{db_name}'")
        return True
    except pyodbc.ProgrammingError:

        return False


def get_mssql_stat_info(sql_conn, db_name) -> str:
    sql_q = 'select TOP(1) restore_date from msdb.dbo.restorehistory ' \
            'where destination_database_name = ? order by restore_date desc '
    with sql_conn.cursor() as curs:
        curs.execute(sql_q, [db_name])
        data = curs.fetchall()
        if data:
            last_recovery_date = data[0][0]
            last_recovery_date = last_recovery_date.strftime('%d-%m-%Y %H:%M')
        else:
            last_recovery_date = "БД не восстанавливалась ранее"

    return last_recovery_date


def get_smb_stat_info(smb_conn, db_name):
    nic = get_nic_name_tuple(db_name)[0]
    # smb_path = f'{config.arh_dict[nic]["smb_path"]}\\BD\\{config.arh_dict[nic]["arh_name"]}\\ARH\\backup_6\\'
    smb_path = f'{config.arh_dict[nic]["smb_path"]}/BD/{config.arh_dict[nic]["arh_name"]}/ARH/backup_6/' ##debian
    file_name = smb_conn.listPath(config.arh_dict[nic]['smb_name'], smb_path)
    smb_conn.close()
    dat = file_name[len(file_name) - 1].filename[-16:-4]
    # dat = {'year': dat[:4], 'month': dat[6:8], 'day': dat[4:6], 'time': f'{dat[8:10]} : {dat[10:12]}'}
    format_data = f"{dat[4:6]}-{dat[6:8]}-{dat[:4]} {dat[8:10]}:{dat[10:12]}"

    return format_data


@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def index():
    form = LoginValidation()
    if request.method in 'POST':
        login_id = form.user_name_pid.data
        login_password = form.user_pid_Password.data
        ldap_conn = get_ldap_authentication(login_id, login_password)
        if ldap_conn:
            db_list = ldap_filter(ldap_conn, login_id)
            session['login_name'] = login_id
            for d in db_list:
                session[d] = get_nic_name_tuple(d)[0]

            return render_template('db1.html', db_list=db_list)
        else:
            error_message = f"*** Authentication Failed ***"
            return render_template("error.html", error_message=str(error_message))

    return render_template('index.html', form=form)


@app.route('/DataBase/<db>', methods=['GET', 'POST'])
def db2(db):
    error_message = f"*** Authentication Failed ***"
    if 'login_name' in session:
        return render_template('db2.html', sql_info=get_mssql_stat_info(get_mssql_conn(session[db]), db),
                               smb_info=get_smb_stat_info(get_smb_conn(session[db]), db),
                               db_name=db)
    else:
        return render_template("error.html", error_message=str(error_message))


@app.route('/DataBase/<path:r>')
def db3(r):
    error_message = f"*** Authentication Failed ***"
    db = r[37:]
    db_restore_time = datetime.datetime.now().replace(microsecond=0)
    if session['login_name']:
        st = f'GOOD! User {session["login_name"]} start recovery DB: {db} in {db_restore_time}'
        log_db_recovery(st)
        del session['login_name']
        return render_template('db3.html',
                               start=start_mssql_sp_start_job(get_mssql_conn(get_nic_name_tuple(db)[0]), r[37:]))
    else:
        st = f'!!!FAIL!!!. User {session["login_name"]} NOT start recovery DB: {db} in {db_restore_time}'
        log_db_recovery(st)
        return render_template("error.html", error_message=str(error_message))


