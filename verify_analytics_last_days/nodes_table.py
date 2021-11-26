"""
    An iterable object of Nodes Instances' settings
"""

from os.path import join as path_join

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
        return 'mysql parameters...'

    @classmethod
    def parse(cls, connection_string):
        """Parse & Return settings obj. by connection string

            @param connection_string:   `sudo mysql learning-abbott_edxapp -u learning-abbott_admin -p -h platform.eu-west-1.rds.amazonaws.com`
            @type connection_string:    string
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

    def release(self):
        """Release resources"""
        if self.__ssl_connection:
            self.__ssl_connection.close()
            self.__ssl_connection = None


class _EC2Node(object):
    """Setting class"""
    def __init__(self, name, type, cert_folder):
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


class Nodes(object):
    LINETYPE_UNKNOW = 0             # Unknow line type, maybe it's a empty line

    LINETYPE_FRENCH_NODE = 1        # French Node Type
    LINETYPE_AMERICA_NODE = 2       # US Node Type

    LINETYPE_SSH_SETTING = 3        # ssh connection string
    LINETYPE_MYSQL_SETTING = 4      # mysql connection string

    def __init__(self, config_file_path, cert_folder):
        """Constructor

            @param config_file_path:        nodes settings file path ( conf/nodes.txt )
            @type config_file_path:         string
            @param cert_folder:             ssl cert pem file folder
            @type cert_folder:              string
        """
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

    def __judge_line_type(self, content):
        """We could know the record content type according to the 'keywords' in string.

            @param content:                 content string of file
            @type content:                  string
            @return:                        enumarate value (setting TYPE)
            @rtype:                         integer
        """
        if len(content) < 1:
            return Nodes.LINETYPE_UNKNOW

        lower_case_prefix_line = content[:10].lower()
        if 'fr' in lower_case_prefix_line and '#' in lower_case_prefix_line and '>' in lower_case_prefix_line:
            return Nodes.LINETYPE_FRENCH_NODE
        elif 'us' in lower_case_prefix_line and '#' in lower_case_prefix_line and '>' in lower_case_prefix_line:
            return Nodes.LINETYPE_AMERICA_NODE
        elif 'ssh ' in lower_case_prefix_line and '-i ' in lower_case_prefix_line:
            return Nodes.LINETYPE_SSH_SETTING
        elif 'mysql ' in lower_case_prefix_line and '-u ' in lower_case_prefix_line:
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
                        self._ec2node_table.append(current_node)

                    elif current_line_type == Nodes.LINETYPE_AMERICA_NODE:
                        self._us_nodes_count += 1
                        current_node = _EC2Node(
                            name=record,
                            type=Nodes.LINETYPE_AMERICA_NODE,
                            cert_folder=self._cert_folder
                        )
                        # ######### Append US Configuration Node #########
                        self._ec2node_table.append(current_node)

                    elif current_line_type == Nodes.LINETYPE_SSH_SETTING:
                        current_node.parse_ssl_connection(record)

                    elif current_line_type == Nodes.LINETYPE_MYSQL_SETTING:
                        current_node.parse_mysql_connection(record)

                record = file_obj.readline()
