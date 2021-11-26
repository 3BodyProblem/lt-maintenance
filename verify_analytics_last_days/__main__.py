"""
	The entry of module.

	A Simple tool of analytics status checking.

	[Usage]:

		`python -m verify_analytics_last_days`
		`python -m verify_analytics_last_days --cert_folder=/Users/barrypaneer/.ssh/`

"""

from argparse import ArgumentParser
from os.path import (
	dirname as file_dirname,
	join as path_join,
	exists as path_exists
)
from sys import exit as process_terminate
from traceback import format_exc

from django.core.exceptions import ValidationError

from nodes_table import Nodes
from verification import Verification


if __name__ == "__main__":
	try:
		# Checking local configuration
		SUBPATH_OF_SETTINGS = r'conf/nodes.txt'
		config_file_path = path_join(file_dirname(__file__), SUBPATH_OF_SETTINGS)
		print(r'[Config file path]: {file_path}'.format(file_path=config_file_path))

		if not path_exists(config_file_path):
			raise ValidationError(
				r'[Error] Invalid config file path: {}'.format(config_file_path)
			)

		# Parsing arguments
		parser = ArgumentParser(description=r'A Simple tool of analytics status checking.')
		parser.add_argument(
			'--cert_folder', default='', help="folder of ssl cert pem files.",
		)
		args = parser.parse_args()
		if not path_exists(args.cert_folder):
			raise ValidationError(
				r'[Error] Invalid SSL Pem key folder: {}'.format(args.cert_folder)
			)

		# Execute
		nodes_settings = Nodes(config_file_path, args.cert_folder)
		verifier = Verification(nodes_settings)
		verifier.execute()

		print(r'[DONE]')

	except Exception:
		print(r'[Exception]: {err_msg}'.format(err_msg=format_exc()))
		process_terminate(10)
