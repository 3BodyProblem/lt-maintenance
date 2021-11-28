"""
	The entry of module.

	A Simple tool of analytics status checking.

	[Usage]:

		`python -m verify_analytics_last_days --cert_folder=/Users/barrypaneer/.ssh/  --fr_mysql_pswd=[...] --us_mysql_pswd=[...]`

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
		parser.add_argument(
			'--fr_mysql_pswd', default=None, help="Mysql pswd of French Nodes",
		)
		parser.add_argument(
			'--us_mysql_pswd', default=None, help="Mysql pswd of United States Nodes",
		)
		args = parser.parse_args()
		if not path_exists(args.cert_folder):
			raise ValidationError(
				r'[Error] Invalid SSL Pem key folder: {}'.format(args.cert_folder)
			)
		if not args.fr_mysql_pswd or not args.us_mysql_pswd:
			raise ValidationError(
				r'[Error] Invalid MySql password of FR/US nodes: {} / {}'.format(
					args.fr_mysql_pswd, args.us_mysql_pswd
				)
			)

		# Execute verification
		with Nodes(config_file_path, args.cert_folder) as ec2nodes:
			Verification(
				ec2nodes[:1],
				args.fr_mysql_pswd,
				args.us_mysql_pswd
			).execute()

		print(r'[DONE]')

	except Exception:
		print(r'[Exception]: {err_msg}'.format(err_msg=format_exc()))
		process_terminate(10)
