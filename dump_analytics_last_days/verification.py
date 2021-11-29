"""
    Verification of analytics

"""

from time import sleep


class _MySqlCommander(object):
    """Mysql login & query commander wrapper class."""
    def __init__(self, ssl_session, mysql_connection_settings, login_password):
        self._shell_session = ssl_session.invoke_shell()
        self._mysql_connection_settings = mysql_connection_settings
        self._ssl_stdin = None
        self._ssl_stdout = None
        self._ssl_stderr = None
        self._login_password = login_password

    def _sync_exe_command(self, cmd):
        """Execute & Return response of command

            @param cmd:                 command string for error message
            @type cmd:                  string
        """
        self._shell_session.sendall(cmd + '\n')

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
        print(resp)
        if r'mysql>' not in resp:
            raise ValueError(
                r'[Login Exception] {} : {}'.format(
                    self._mysql_connection_settings.connection_string.replace(' -p ', ' -p{} '.format(login_password)),
                    resp
                )
            )

    def _verify_analytics_by_date(self):
        """Verify analytics compiled correctly in the past days"""
        sql = r'select * from triboo_analytics_reportlog where date(created)>="2021-11-22";'
        resp = self._sync_exe_command(sql)
        if 'modified' not in resp or 'learner_visit' not in resp or 'learner_course' not in resp:
            raise ValueError(
                r'[Query Exception] {} : {}'.format(sql, resp)
            )

    def execute(self):
        self._login(self._login_password)
        self._verify_analytics_by_date()


class Verification(object):
    """Verification of analytics."""
    def __init__(self, ec2nodes, fr_mysql_pswd, us_mysql_pswd):
        """Constrctor

            @param ec2nodes:      nodes settings of Mysql / SSL of each AWS Node Instances.
            @type ec2nodes:       iterable object.
        """
        self._ec2nodes = ec2nodes
        self._fr_mysql_pswd = fr_mysql_pswd
        self._us_mysql_pswd = us_mysql_pswd

    def execute(self):
        """Execute verification for each EC2 Node."""
        for node in self._ec2nodes:
            print(r'[Verifing EC2 Node] ===> {}'.format(node))
            _MySqlCommander(
                node.ssl_session,
                node.mysql_interactive_command,
                self._fr_mysql_pswd if node.type() == 1 else self._us_mysql_pswd    # Choose Pswd by node Type
            ).execute()
