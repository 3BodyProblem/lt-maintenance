"""
	The entry of module.
"""

from django.core.exceptions import ValidationError
from os.path import (
	dirname as file_dirname,
	join as path_join,
	exists as path_exists
)
from sys import exit as process_terminate
from traceback import format_exc


from nodes_table import NodesSettings
from verification import Verification


if __name__ == "__main__":
	try:
		SUBPATH_OF_SETTINGS = r'conf/nodes.txt'
		config_file_path = path_join(file_dirname(__file__), SUBPATH_OF_SETTINGS)
		print(r'[Config file path]: {file_path}'.format(file_path=config_file_path))

		if not path_exists(config_file_path):
			raise ValidationError(
				r'[Error] Invalid config file path: {}'.format(config_file_path)
			)
		nodes_settings = NodesSettings(config_file_path)
		verifier = Verification(nodes_settings)
		verifier.execute()

		print(r'[DONE]')

	except Exception:
		print(r'[Exception]: {err_msg}'.format(err_msg=format_exc()))
		process_terminate(10)
