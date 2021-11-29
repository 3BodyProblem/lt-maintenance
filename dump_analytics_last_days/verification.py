"""
    Verification of analytics

"""

from time import sleep
from traceback import format_exc


class _MySqlCommander(object):
    """Mysql login & query commander wrapper class."""
    SQL_QUERY_REPORTLOG = r'SELECT * FROM triboo_analytics_reportlog WHERE date(created)>="{}";'

    def __init__(self, ssl_session, mysql_connection_settings, login_password, since):
        self._shell_session = ssl_session.invoke_shell()
        self._mysql_connection_settings = mysql_connection_settings
        self._ssl_stdin = None
        self._ssl_stdout = None
        self._ssl_stderr = None
        self._since = since
        self._login(login_password)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._logout()

    def _sync_exe_command(self, cmd):
        """Execute & Return response of command

            @param cmd:                 command string for error message
            @type cmd:                  string
        """
        self._shell_session.sendall(cmd + '\n')
        sleep(1)

        for i in range(1, 60):
            sleep(1)

            if self._shell_session.recv_ready():
                return self._shell_session.recv(1024 * 1024 * 3)

        raise ValueError(r'[TIMEOUT] : {}'.format(cmd))

    def _login(self, login_password):
        """Establish a Mysql Login Session

            @param login_password:      Mysql Login Password
            @type login_password:       string
        """
        print(r'[Login Mysql with command] {}'.format(self._mysql_connection_settings.connection_string))

        resp = self._sync_exe_command(
            self._mysql_connection_settings.connection_string.replace(' -p ', ' -p{} '.format(login_password))
        )
        if r'mysql>' not in resp:
            raise ValueError(
                r'[Login Exception] {} : {}'.format(
                    self._mysql_connection_settings.connection_string.replace(' -p ', ' -p{} '.format(login_password)),
                    resp
                )
            )

    def _logout(self):
        """Logout Mysql session"""
        try:
            resp = self._sync_exe_command(r'exit;')
            if 'Bye' not in resp:
                raise ValueError('Failed to logout: {}'.format(resp))
        except Exception:
            print(r'[Exception occur while Logout]: {err_msg}'.format(err_msg=format_exc()))

    def _verify_analytics_by_date(self):
        """Verify analytics compiled correctly in the past days"""
        sql = _MySqlCommander.SQL_QUERY_REPORTLOG.format(self._since)
        resp = self._sync_exe_command(sql)
        if 'modified' not in resp or 'learner_visit' not in resp or 'learner_course' not in resp:
            raise ValueError(
                r'[Query Exception] {} : {}'.format(sql, resp)
            )
        print(resp)

    def execute(self):
        self._verify_analytics_by_date()


class Verification(object):
    """Verification of analytics."""
    def __init__(self, ec2nodes, fr_mysql_pswd, us_mysql_pswd, since):
        """Constrctor

            @param ec2nodes:        nodes settings of Mysql / SSL of each AWS Node Instances.
            @type ec2nodes:         iterable object.
            @param fr_mysql_pswd:   mysql password of frech nodes
            @type fr_mysql_pswd:    string
            @param us_mysql_pswd:   mysql password of US nodes
            @type us_mysql_pswd:    string
            @param since:           first checking date (Sample: 2021-11-22)
            @type since:            string

        """
        self._ec2nodes = ec2nodes
        self._fr_mysql_pswd = fr_mysql_pswd
        self._us_mysql_pswd = us_mysql_pswd
        self._since = since

    def execute(self):
        """Execute verification for each EC2 Node."""
        for node in self._ec2nodes:
            print(r'[Verifing EC2 Node] ===> {}'.format(node))
            with _MySqlCommander(
                node.ssl_session,
                node.mysql_interactive_command,
                self._fr_mysql_pswd if node.type() == 1 else self._us_mysql_pswd,    # Choose Pswd by node Type
                self._since
            ) as cmd:
                cmd.execute()
