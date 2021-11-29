"""
	The entry of module.

	A Simple tool of analytics status checking.

	[Workflow]:
		Input Args: `ssl cert folder` + `US / FR Mysql Password` + `since date`
		Output: A SSL Shell Echo dump file (Sample `lt-maintenance/dump_analytics_last_days/analytics_2021-11-22.dump`)

		1. Loading nodes SSL connection & Mysql settings from `conf/nodes.txt`. (Pls update the nodes.txt from `https://github.com/Learningtribes/delivery`)
		2. Iterate & verify Mysql Table with SSL Shell One EC2 Node By One.
		3. Dumping all of the echo content from Each Node Shell.
		4. Then, user check the dump file (Sample: .../analytics_2021-11-22.dump) manually.
			- Including Error/Exception for Each Node.
			- Including Query Result of Mysql Table `triboo_analytics_reportlog` of Each Node.

		Sample of dump file as follow:
			# FR > Abbott >>>>>>>>>>>
			SELECT * FROM triboo_analytics_reportlog WHERE date(created)>="2021-11-22 ^H";
			+-----+----------------------------+----------------------------+----------------------------+----------------------------+----------------------------+----------------------------+----------------------------+----------------------------+
			| id  | created                    | modified                   | learner_visit              | learner_course             | learner                    | course                     | microsite                  | country                    |
			+-----+----------------------------+----------------------------+----------------------------+----------------------------+----------------------------+----------------------------+----------------------------+----------------------------+
			| 119 | 2021-11-22 01:40:06.906722 | 2021-11-22 01:40:13.224861 | 2021-11-22 01:40:06.901095 | 2021-11-22 01:40:12.662131 | 2021-11-22 01:40:12.999630 | 2021-11-22 01:40:13.081538 | 2021-11-22 01:40:13.153081 | 2021-11-22 01:40:13.222970 |
			| 120 | 2021-11-23 01:40:06.439054 | 2021-11-23 01:40:09.939896 | 2021-11-23 01:40:06.430946 | 2021-11-23 01:40:09.648886 | 2021-11-23 01:40:09.812521 | 2021-11-23 01:40:09.858002 | 2021-11-23 01:40:09.899777 | 2021-11-23 01:40:09.937358 |
			| 121 | 2021-11-24 01:40:06.720530 | 2021-11-24 01:40:11.557364 | 2021-11-24 01:40:06.713794 | 2021-11-24 01:40:11.218092 | 2021-11-24 01:40:11.394345 | 2021-11-24 01:40:11.460681 | 2021-11-24 01:40:11.514731 | 2021-11-24 01:40:11.555625 |
			...
			...
			...
		5. Releasing SSL handles & Mysql connections.

	[Usage]:

		- `python -m dump_analytics_last_days --cert_folder=/Users/barrypaneer/.ssh/  --fr_mysql_pswd=[...] --us_mysql_pswd=[...] --since=2021-11-22`
		- Check Error Logs in Screen ( Some Node may got failure because of Unstable SSL connection )
		- Check dump file: dump_analytics_last_days/analytics_2021-aa-bb.dump

"""

# *** We Patched all at the TOP line. ***
from gevent import monkey; monkey.patch_all()

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
			'--cert_folder', default='', help='folder of ssl cert pem files.'
		)
		parser.add_argument(
			'--fr_mysql_pswd', default=None, help='Mysql pswd of French Nodes'
		)
		parser.add_argument(
			'--us_mysql_pswd', default=None, help='Mysql pswd of United States Nodes'
		)
		parser.add_argument(
			'--since', default=None, help='The first date for dumping'
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
		if not args.since:
			raise ValidationError(r'[Error] Pls specify `first checking date` with `--since=...` ')

		# Execute verification
		with Nodes(config_file_path, args.cert_folder) as ec2nodes:
			Verification(
				ec2nodes,
				args.fr_mysql_pswd,
				args.us_mysql_pswd,
				args.since
			).execute()

		print(r'[DONE]')

	except Exception:
		print(r'[Exception]: {err_msg}'.format(err_msg=format_exc()))
		process_terminate(10)
