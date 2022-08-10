"""
    An iterable object of Nodes Instances' settings
"""

from os.path import join as path_join
from traceback import format_exc

from paramiko import (
    AutoAddPolicy,
    RSAKey,
    SSHClient
)


class _Mysql_Setting(object):
    """Settings of Mysql connecton"""
    def __init__(self, mysql_connection_string):
        """Constructor. Save mysql connection raw string"""
        self._mysql_connection_string = mysql_connection_string

    def __str__(self):
        return self._mysql_connection_string

    @property
    def connection_string(self):
        """Return mysql connection string WITHOUT password"""
        return self._mysql_connection_string

    @classmethod
    def parse(cls, connection_string):
        """Parse & Return settings obj. by connection string

            @param connection_string:   `sudo mysql learning-abbott_edxapp -u learning-abbott_admin -p -h platform.eu-west-1.rds.amazonaws.com`
            @type connection_string:    string
            @return:                    New Instance
            @rtype:                     _Mysql_Setting

        """
        if not connection_string:
            raise ValueError(r'invalid mysql settings : {}'.format(connection_string))

        return _Mysql_Setting(connection_string)


class _SSL_Client(object):
    """Settings of SSL connection"""
    def __init__(self, key_file_path, host, user_name):
        """Constructor

            @param key_file_path:       the path of ssl cert key file.
            @type key_file_path:        string
            @param host:                ssl server host
            @type host:                 string
            @param user_name:           ssl login user name
            @type user_name:            string
        """
        self.__key_file_path = key_file_path
        self.__host = host
        self.__user_name = user_name
        self.__ssl_connection = None

    def __str__(self):
        return r'host:{} '.format(self.__host)

    @classmethod
    def parse(cls, connection_string, cert_folder):
        """Parse & Return settings obj. by connection string

            @param connection_string:   `ssh -i eu-west-1_platform_key.pem -o ServerAliveInterval=45 ubuntu@3.249.4.219`
            @type connection_string:    string
            @return:                    New Instance
            @rtype:                     _SSL_Client

        """
        if not connection_string:
            raise ValueError(r'invalid ssl settings : {}'.format(connection_string))

        # ssl .pem file
        i = connection_string.find(r' -i ')
        located_string = connection_string[i + 4:]
        i = located_string.find(r' ')
        _cert_key_file = located_string[:i]

        # ssl TTL interval value
        i = connection_string.find(r' -o ')
        located_string = connection_string[i + 4:]
        i = located_string.find(r' ')
        located_string = located_string[:i]
        i = located_string.find('=')
        _ttl_interval = int(located_string[i+1:])

        # ssl login name
        _user_name = r'ubuntu'
        # ssl host
        i = connection_string.find(_user_name+r'@')
        _host = connection_string[i+7:].strip()

        _cert_key_file = path_join(cert_folder, _cert_key_file) \
            if cert_folder \
            else _cert_key_file
        return _SSL_Client(_cert_key_file, _host, _user_name)

    @classmethod
    def gen_ssl_connection(cls, key_file_path, host, user_name):
        """Generate ssl connection by ssl `cert key file` & host & `login name`"""
        file_key = RSAKey.from_private_key_file(key_file_path)
        new_conn_obj = SSHClient()

        new_conn_obj.set_missing_host_key_policy(AutoAddPolicy())
        new_conn_obj.connect(hostname=host, username=user_name, pkey=file_key)

        return new_conn_obj

    @property
    def session(self):
        """Return ssl connection obj."""
        if not self.__ssl_connection:
            self.__ssl_connection = _SSL_Client.gen_ssl_connection(
                self.__key_file_path,
                self.__host,
                self.__user_name
            )
        return self.__ssl_connection

    def release(self):
        """Release resources"""
        try:
            if self.__ssl_connection:
                self.__ssl_connection.close()
                self.__ssl_connection = None

            return True

        except Exception:
            print(r'[Exception occur while Releasing Resourses]: {err_msg}'.format(err_msg=format_exc()))
            return False


class _EC2Node(object):
    """Setting class"""
    def __init__(self, name, type, cert_folder):
        """Construct & hold instance config for a site node
        """
        if type not in (Nodes.LINETYPE_FRENCH_NODE, Nodes.LINETYPE_AMERICA_NODE):
            raise ValueError(r'[Error] Invalie node type : {}'.format(type))

        self._name = name.replace('\n', '').replace('\r', '')
        self._type = type
        self._cert_folder = cert_folder
        self._ssl_client = None
        self._mysql_setting = None

    def __str__(self):
        return r'[{}] ssl: {} mysql: {}'.format(
            self._name, self._ssl_client, self._mysql_setting
        )

    def name(self):
        """Node name, like: `Abbott`"""
        return self._name

    def type(self):
        """Node type, like: Nodes.LINETYPE_FRENCH_NODE / LINETYPE_AMERICA_NODE"""
        return self._type

    def parse_ssl_connection(self, content):
        """Parse Ssl connection from string"""
        self._ssl_client = _SSL_Client.parse(content, self._cert_folder)

    def parse_mysql_connection(self, content):
        """Parse Mysql connection from string"""
        self._mysql_setting = _Mysql_Setting.parse(content)

    @property
    def ssl_session(self):
        """Return ssl connection session."""
        if not self._ssl_client:
            return None

        return self._ssl_client.session

    @property
    def mysql_interactive_command(self):
        """Return mysql interative command line string"""
        if not self._mysql_setting:
            return None

        return self._mysql_setting

    def release(self):
        """Release all resourses.

            @return:        Return `True` if released all resourses.
            @rtype:         boolean
        """
        _ssl_released = True
        if self._ssl_client:
            _ssl_released = self._ssl_client.release()

        return _ssl_released


class Nodes(object):
    LINETYPE_UNKNOW = 0             # Unknow line type, maybe it's a empty line

    LINETYPE_FRENCH_NODE = 1        # French Node Type
    LINETYPE_AMERICA_NODE = 2       # US Node Type

    LINETYPE_SSH_SETTING = 3        # ssh connection string
    LINETYPE_MYSQL_SETTING = 4      # mysql connection string

    def __init__(self, config_file_path, cert_folder, specified_nodes):
        """Constructor

            @param config_file_path:        nodes settings file path ( conf/nodes.txt )
            @type config_file_path:         string
            @param cert_folder:             ssl cert pem file folder
            @type cert_folder:              string
        """
        self._specified_nodes = specified_nodes.split(',') if specified_nodes else None
        self._cert_folder = cert_folder
        self._fr_nodes_count = 0
        self._us_nodes_count = 0
        self._ec2node_table = []
        self.__build_settings(config_file_path)

        print(
            '[STAT INFO] US Nodes count: {} + FR Nodes count: {} = Total Len: {}'.format(
                self._us_nodes_count, self._fr_nodes_count, len(self._ec2node_table)
            )
        )

    def __iter__(self):
        """Return iterable object"""
        return iter(self._ec2node_table)

    def __getitem__(self, item_index):
        """Return item reference by index number"""
        return self._ec2node_table[item_index]

    def __enter__(self):
        """Return self handle of this instance."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Support content manager."""
        print(r'[Releasing resouses (ssl / mysql)]')

        for ec2node in self._ec2node_table:
            ec2node.release()

    def _is_specified_node(self, es_node_name):
        if not self._specified_nodes:
            return True

        for _name in self._specified_nodes:
            if _name in es_node_name:
                return True

        return False

    def __judge_line_type(self, content):
        """We could know the record content type according to the 'keywords' in string.

            @param content:                 content string of file
            @type content:                  string
            @return:                        enumarate value (setting TYPE)
            @rtype:                         integer
        """
        if len(content) < 1:
            return Nodes.LINETYPE_UNKNOW

        content = content.lower()

        if '# fr >' in content and '#' in content and '>' in content:
            return Nodes.LINETYPE_FRENCH_NODE
        elif '# us >' in content and '#' in content and '>' in content:
            return Nodes.LINETYPE_AMERICA_NODE
        elif 'ssh ' in content and '-i ' in content:
            return Nodes.LINETYPE_SSH_SETTING
        elif 'mysql ' in content and '-u ' in content:
            return Nodes.LINETYPE_MYSQL_SETTING

    def __build_settings(self, conf_file):
        """Build nodes' settings list

            @param conf_file:               nodes settings file path ( conf/nodes.txt )
            @type conf_file:                string
            @return:                        return list of nodes settings
            @rtype:                         list
        """
        with open(conf_file) as file_obj:
            current_node = None
            record = file_obj.readline()

            while record:
                current_line_type = self.__judge_line_type(record)

                if current_line_type != Nodes.LINETYPE_UNKNOW:
                    # print(record)
                    if current_line_type == Nodes.LINETYPE_FRENCH_NODE:
                        self._fr_nodes_count += 1
                        current_node = _EC2Node(
                            name=record,
                            type=Nodes.LINETYPE_FRENCH_NODE,
                            cert_folder=self._cert_folder
                        )
                        # ######### Append FR Configuration Node #########
                        if self._is_specified_node(current_node.name()):
                            self._ec2node_table.append(current_node)

                    elif current_line_type == Nodes.LINETYPE_AMERICA_NODE:
                        self._us_nodes_count += 1
                        current_node = _EC2Node(
                            name=record,
                            type=Nodes.LINETYPE_AMERICA_NODE,
                            cert_folder=self._cert_folder
                        )
                        # ######### Append US Configuration Node #########
                        if self._is_specified_node(current_node.name()):
                            self._ec2node_table.append(current_node)

                    elif current_line_type == Nodes.LINETYPE_SSH_SETTING:
                        if self._is_specified_node(current_node.name()):
                            current_node.parse_ssl_connection(record)

                    elif current_line_type == Nodes.LINETYPE_MYSQL_SETTING:
                        if self._is_specified_node(current_node.name()):
                            current_node.parse_mysql_connection(record)

                record = file_obj.readline()
