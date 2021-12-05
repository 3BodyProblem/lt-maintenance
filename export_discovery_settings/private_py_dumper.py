from json import load as load_json_file
from os.path import (
    basename,
    exists as file_exists,
    isfile,
    join as path_join,
    normpath
)


class FilePrivatePyDumper(object):
    """Python cfg file `private.py` generator

        Input file:     `hawthorn_inventory/configuration_files/xxx_123/discovery.auth.json`
        Output file:    `output/xxx_123_private.py`

    """
    OUTPUT_FILE_NAME = r'_private.py'
    OUTPUT_FILE_TEMPLATE = u"""DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "HOST": "{HOST}",
        "NAME": "{NAME}",
        "PASSWORD": "{PASSWORD}",
        "PORT": "3306",
        "USER": "{USER}"
    }
}"""
    CFG_FILE_DISCOVERY_NAME = r'discovery.auth.json'

    def __init__(self, node_config_folder, output_folder):
        """Constructor

            @param node_config_folder:      node config folder
            @type node_config_folder:       string
            @param output_folder:           output file folder
            @type output_folder:            string

        """
        _tail_folder_name = basename(
            normpath(node_config_folder)
        )
        self._output_file_path = path_join(
            output_folder,
            _tail_folder_name + FilePrivatePyDumper.OUTPUT_FILE_NAME
        )
        self._node_config_file = path_join(
            node_config_folder,
            FilePrivatePyDumper.CFG_FILE_DISCOVERY_NAME
        )

        if not file_exists(self._node_config_file):
            raise Exception(
                r'[Error] file ({missed_file}) does not exist.'.format(missed_file=self._node_config_file)
            )
        if not isfile(self._node_config_file):
            raise Exception(
                r'[Error] invalid file: {invalid_file}.'.format(invalid_file=self._node_config_file)
            )

    def dump(self):
        utf_8_template_content = FilePrivatePyDumper.OUTPUT_FILE_TEMPLATE.encode('utf-8')

        with open(self._node_config_file) as f:
            json_obj_with_unicode = load_json_file(f)
            cfg = json_obj_with_unicode['DATABASES']['default']

            with open(self._output_file_path, 'w') as o:
                utf_8_template_content = utf_8_template_content.replace(r'{HOST}', cfg['HOST'])
                utf_8_template_content = utf_8_template_content.replace(r'{NAME}', cfg['NAME'])
                utf_8_template_content = utf_8_template_content.replace(r'{PASSWORD}', cfg['PASSWORD'])
                utf_8_template_content = utf_8_template_content.replace(r'{USER}', cfg['USER'])

                o.write(utf_8_template_content)
