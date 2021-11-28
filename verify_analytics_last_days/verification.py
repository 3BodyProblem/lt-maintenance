"""
    Verification of analytics

"""


class _MySqlCommander(object):
    """Mysql login & query commander wrapper class."""
    def __init__(self, ssl_session, mysql_connection_settings, login_password):
        self._ssl_session = ssl_session
        self._mysql_connection_settings = mysql_connection_settings
        self._ssl_stdin = None
        self._ssl_stdout = None
        self._ssl_stderr = None
        self._login(login_password)

    def _login(self, login_password):
        """establish a Mysql Login Session

            @param login_password:      Mysql Login Password
            @type login_password:       string
        """
        print(r'[Login Mysql with command] {}'.format(self._mysql_connection_settings.connection_string))
        print(self._mysql_connection_settings.connection_string.replace(' -p ', ' -p{} '.format(login_password)))

        self._ssl_stdin, self._ssl_stdout, self._ssl_stderr = self._ssl_session.exec_command(
            self._mysql_connection_settings.connection_string.replace(' -p ', ' -p{} '.format(login_password))
        )
        print(r'{}'.format(self._ssl_stdout.read()))
        # ssh_stdin.write('password\n')
        # ssh_stdin.flush()
        # output = ssh_stdout.read()


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
            cmd = _MySqlCommander(
                node.ssl_session,
                node.mysql_interactive_command,
                self._fr_mysql_pswd if node.type() == 1 else self._us_mysql_pswd    # Choose Pswd by node Type
            )
