"""
    An iterable object of Nodes Instances' settings
"""


class _Mysql_Setting(object):
    @classmethod
    def parse(cls, content):
        pass


class _SSL_Setting(object):
    @classmethod
    def parse(cls, content):
        pass


class _Setting(object):
    """Setting class"""
    def __init__(self, name, type):
        self._name = name
        self._type = type
        self._ssl_setting = None
        self._mysql_setting = None

    def name(self):
        """Node name, like: `Abbott`"""
        return self._name

    def type(self):
        """Node type, like: NodesSettings.LINETYPE_FRENCH_NODE / LINETYPE_AMERICA_NODE"""
        return self._type

    def parse_ssl_connection(self, content):
        """Parse Ssl connection from string"""
        self._ssl_setting = _SSL_Setting.parse(content)

    def parse_mysql_connection(self, content):
        """Parse Mysql connection from string"""
        self._mysql_setting = _Mysql_Setting.parse(content)


class NodesSettings(object):
    LINETYPE_UNKNOW = 0             # Unknow line type, maybe it's a empty line

    LINETYPE_FRENCH_NODE = 1        # French Node Type
    LINETYPE_AMERICA_NODE = 2       # US Node Type

    LINETYPE_SSH_SETTING = 3        # ssh connection string
    LINETYPE_MYSQL_SETTING = 4      # mysql connection string

    def __init__(self, config_file_path):
        """Constructor

            @param config_file_path:        nodes settings file path ( conf/nodes.txt )
            @type config_file_path:         string
        """
        self._fr_nodes_count = 0
        self._us_nodes_count = 0
        self._settings_table = []
        self._build_settings(config_file_path)

        print(
            '[STAT INFO] US Nodes count: {} + FR Nodes count: {} = Total Len: {}'.format(
                self._us_nodes_count, self._fr_nodes_count, len(self._settings_table)
            )
        )

    def _judge_line_type(self, content):
        """We could know the record content type according to the 'keywords' in string.

            @param content:                 content string of file
            @type content:                  string
            @return:                        enumarate value (setting TYPE)
            @rtype:                         integer
        """
        if len(content) < 1:
            return NodesSettings.LINETYPE_UNKNOW

        lower_case_prefix_line = content[:10].lower()
        if 'fr' in lower_case_prefix_line and '#' in lower_case_prefix_line and '>' in lower_case_prefix_line:
            return NodesSettings.LINETYPE_FRENCH_NODE
        elif 'us' in lower_case_prefix_line and '#' in lower_case_prefix_line and '>' in lower_case_prefix_line:
            return NodesSettings.LINETYPE_AMERICA_NODE
        elif 'ssh ' in lower_case_prefix_line and '-i ' in lower_case_prefix_line:
            return NodesSettings.LINETYPE_SSH_SETTING
        elif 'mysql ' in lower_case_prefix_line and '-u ' in lower_case_prefix_line:
            return NodesSettings.LINETYPE_MYSQL_SETTING

    def _build_settings(self, conf_file):
        """Build nodes' settings list

            @param conf_file:               nodes settings file path ( conf/nodes.txt )
            @type conf_file:                string
            @return:                        return list of nodes settings
            @rtype:                         list
        """
        with open(conf_file) as file_obj:
            current_setting = None
            record = file_obj.readline()

            while record:
                current_line_type = self._judge_line_type(record)
                if current_line_type != NodesSettings.LINETYPE_UNKNOW:
                    # print(record)
                    if current_line_type == NodesSettings.LINETYPE_FRENCH_NODE:
                        self._fr_nodes_count += 1
                        current_setting = _Setting(
                            name=record, type=NodesSettings.LINETYPE_FRENCH_NODE
                        )
                        self._settings_table.append(current_setting)
                    elif current_line_type == NodesSettings.LINETYPE_AMERICA_NODE:
                        self._us_nodes_count += 1
                        current_setting = _Setting(
                            name=record, type=NodesSettings.LINETYPE_AMERICA_NODE
                        )
                        self._settings_table.append(current_setting)
                    elif current_line_type == NodesSettings.LINETYPE_SSH_SETTING:
                        current_setting.parse_ssl_connection(record)
                    elif current_line_type == NodesSettings.LINETYPE_MYSQL_SETTING:
                        current_setting.parse_mysql_connection(record)

                record = file_obj.readline()
