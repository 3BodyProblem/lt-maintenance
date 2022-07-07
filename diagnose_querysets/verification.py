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
    SQL_QUERY_REPORTLOG = r'SELECT * FROM triboo_analytics_reportlog WHERE date(created)>="{}";'

    def __init__(self, node_name, ssl_session, mysql_connection_settings, login_password, query_sql, dump_file):
        self._echo_content = r'{} {}'.format(node_name, ' >>>>>>>>>>> \r\n')
        self._dump_file = dump_file
        self._node_name = node_name
        self._shell_session = ssl_session.invoke_shell()
        self._mysql_connection_settings = mysql_connection_settings
        self._ssl_stdin = None
        self._ssl_stdout = None
        self._ssl_stderr = None
        self._query_sql = query_sql
        self._login_flag = False
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

    def _sync_exe_command(self, cmd, raise_exc_flag=False):
        """Execute & Return response of command

            @param cmd:                 command string for error message
            @type cmd:                  string
        """
        try:
            self._shell_session.sendall(cmd + '\n')

            for i in range(1, 60):
                sleep(3)

                if self._shell_session.recv_ready():
                    return self._shell_session.recv(1024 * 1024 * 3)

            raise ValueError(r'[Exception : TIMEOUT] : {}'.format(cmd))

        except Exception:
            self._append_echo_content(cmd)
            if raise_exc_flag:
                raise
            return format_exc()

    def _login(self, login_password):
        """Establish a Mysql Login Session

            @param login_password:      Mysql Login Password
            @type login_password:       string
        """
        try:
            resp = self._sync_exe_command(
                self._mysql_connection_settings.connection_string.replace(' -p ', ' -p{} '.format(login_password)),
                raise_exc_flag=True
            )
            if r'mysql>' not in resp:
                exc_msg = r'[Login Exception] {} : {}'.format(
                    self._mysql_connection_settings.connection_string.replace(' -p ', ' -p{} '.format(login_password)),
                    resp
                )
                self._append_echo_content(exc_msg)
                raise ValueError(exc_msg)

            self._login_flag = True
        except Exception:
            pass

    def _logout(self):
        """Logout Mysql session"""
        try:
            resp = self._sync_exe_command(r'exit;')
            if 'Bye' not in resp:
                raise ValueError('Failed to logout: {}'.format(resp))
        except Exception:
            exc_msg = r'[Exception occur while Logout] : {err_msg}'.format(err_msg=format_exc())
            self._append_echo_content(exc_msg)
            print(exc_msg)

    def _verify_analytics_by_date(self):
        """Verify analytics compiled correctly in the past days"""
        # sql = _MySqlCommander.SQL_QUERY_REPORTLOG.format(self._since)
        resp = self._sync_exe_command(self._query_sql)

        if 'modified' not in resp or 'learner_visit' not in resp or 'learner_course' not in resp:
            exc_msg = r'[Query Exception] {} : {}'.format(self._query_sql, resp)
            self._append_echo_content(exc_msg)
            raise ValueError(exc_msg)
        else:
            self._append_echo_content(resp)

    def execute(self):
        if not self._login_flag:
            return

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

                with _MySqlCommander(
                    node.name(), node.ssl_session,
                    node.mysql_interactive_command,
                    self._fr_mysql_pswd if node.type() == 1 else self._us_mysql_pswd,    # Choose Pswd by node Type
                    self._policy_obj.as_sql(),
                    dump_file=dump_file
                ) as cmd:
                    cmd.execute()

                node.release()
