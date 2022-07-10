"""
    Verification of analytics

"""

from datetime import datetime
from os.path import (
	dirname as file_dirname,
    join as path_join
)
from time import sleep
from traceback import format_exc
from nodes_table import Nodes


class _MySqlCommander(object):
    """Mysql login & query commander wrapper class."""
    INCREMENT_COUNT = 0

    def __init__(self, node_name, ssl_session, mysql_connection_settings, login_password, query_sql, mysql_response_validator, dump_file):
        self._echo_content = r'{} {}'.format(node_name, ' >>>>>>>>>>> \r\n')
        self._dump_file = dump_file
        self._node_name = node_name
        self._shell_session = ssl_session.invoke_shell()
        self._mysql_connection_settings = mysql_connection_settings
        self._ssl_stdin = None
        self._ssl_stdout = None
        self._ssl_stderr = None
        self._query_sql = query_sql
        self._mysql_response_validator = mysql_response_validator
        self._login(login_password)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._logout()
        self._dump_echo_content()

    def _append_echo_content(self, content):
        """Append echo string for dump file"""
        self._echo_content += (content + '\r\n')

    def _dump_echo_content(self):
        """Dump echo info. to local file."""
        _MySqlCommander.INCREMENT_COUNT += 1
        self._dump_file.write('=======> [{}] \r\n'.format(_MySqlCommander.INCREMENT_COUNT))
        self._dump_file.write(self._echo_content)

    def _sync_exe_command(self, cmd, raise_exc_flag=True):
        """Execute & Return response of command ( including Exception ) or raise Exception.

            @param cmd:                 command string for error message
            @type cmd:                  string
        """
        try:
            self._shell_session.sendall(cmd + '\n')

            for i in range(1, 100):
                sleep(1)        # Timeout = 100 Seconds

                if self._shell_session.recv_ready():
                    sleep(6)
                    return self._shell_session.recv(1024 * 1024 * 6)

            raise ValueError(r'[Exception : TIMEOUT] : {}'.format(cmd))

        except Exception:
            if raise_exc_flag:
                raise
            else:
                self._append_echo_content(cmd)

            return format_exc()

    def _login(self, login_password):
        """Establish a Mysql Login Session

            @param login_password:      Mysql Login Password
            @type login_password:       string
        """
        resp = self._sync_exe_command(
            self._mysql_connection_settings.connection_string.replace(' -p ', ' -p{} '.format(login_password))
        )
        if r'mysql>' not in resp and r'MySQL connection id is' not in resp and r'mysql: [Warning]' not in resp:
            exc_msg = r'[Login Exception] {} : {}'.format(
                self._mysql_connection_settings.connection_string.replace(' -p ', ' -p{} '.format(login_password)),
                resp
            )
            raise ValueError(exc_msg)

    def _logout(self):
        """Logout Mysql session & Don't throw any exception"""
        try:
            resp = self._sync_exe_command(r'exit;')
            if 'Bye' not in resp:
                raise ValueError('Failed to logout: {}'.format(resp))
        except Exception:
            print(r'[Exception occur while Logout] : {err_msg}'.format(err_msg=format_exc()))

    def _verify_analytics_by_date(self):
        """Verify analytics compiled correctly in the past days"""
        resp = self._sync_exe_command(self._query_sql)

        err_msg = self._mysql_response_validator(resp)
        if err_msg:
            raise ValueError(err_msg)

        self._append_echo_content(resp)

    def execute(self):
        self._verify_analytics_by_date()


class Verification(object):
    """Verification of analytics."""
    def __init__(self, ec2nodes, fr_mysql_pswd, us_mysql_pswd, policy_obj):
        """Constrctor

            @param ec2nodes:        nodes settings of Mysql / SSL of each AWS Node Instances.
            @type ec2nodes:         iterable object.
            @param fr_mysql_pswd:   mysql password of frech nodes
            @type fr_mysql_pswd:    string
            @param us_mysql_pswd:   mysql password of US nodes
            @type us_mysql_pswd:    string
            @param policy_obj:      instance of policy class
            @type policy_obj:       subclass of class `_QueryPolicyInterface`
        """
        self._ec2nodes = ec2nodes
        self._fr_mysql_pswd = fr_mysql_pswd
        self._us_mysql_pswd = us_mysql_pswd
        self._policy_obj = policy_obj
        # Callback of policy
        self._policy_obj.on_prepare()       # Trigger prepare event

    @property
    def dump_file_path(self):
        return path_join(
            file_dirname(__file__),
            'analytics_{}.dump'.format(datetime.now().strftime("%m-%d-%Y_%H_%M_%S"))
        )

    def execute(self):
        """Execute verification for each EC2 Node."""
        with open(self.dump_file_path, 'w') as dump_file:
            print(r'[Echo Dump File] : {}'.format(self.dump_file_path))

            for node in self._ec2nodes:
                sleep(2)

                if node.type() == Nodes.LINETYPE_FRENCH_NODE and not self._fr_mysql_pswd:
                    continue
                if node.type() == Nodes.LINETYPE_AMERICA_NODE and not self._us_mysql_pswd:
                    continue

                print(node.name())
                retry_flag = True

                while retry_flag:
                    try:
                        with _MySqlCommander(
                            node.name(), node.ssl_session,
                            node.mysql_interactive_command,
                            self._fr_mysql_pswd if node.type() == Nodes.LINETYPE_FRENCH_NODE else self._us_mysql_pswd,# Choose Pswd by node Type
                            self._policy_obj.as_sql(),
                            self._policy_obj.mysql_response_validator,
                            dump_file=dump_file
                        ) as cmd:
                            cmd.execute()

                        retry_flag = False

                    except Exception as _e:
                        user_choice = raw_input(
                            'Got an exception : {}\n Do you wanna retry ? [Y/n] :'.format(str(_e))
                        )
                        user_choice = user_choice.lower()

                        if 'y' == user_choice:
                            retry_flag = True
                        else:
                            retry_flag = False
                            dump_file.write(str(_e))

                dump_file.flush()
                node.release()
