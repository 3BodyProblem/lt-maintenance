"""
	The entry of module.

	A Simple tool of analytics status checking.

	[Workflow]:
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
			...
			...
			...
		5. Releasing SSL handles & Mysql connections.

	[Usage]:
		 - File README.md

"""


from argparse import ArgumentParser
from os.path import (
	dirname as file_dirname,
	join as path_join,
	exists as path_exists
)
from sys import exit as process_terminate
from traceback import format_exc

from nodes_table import Nodes
from query_policy import policy_manager
from verification import Verification


if __name__ == "__main__":
	try:
		# 1. Checking local configuration
		SUBPATH_OF_SETTINGS = r'conf/nodes.txt'
		config_file_path = path_join(file_dirname(__file__), SUBPATH_OF_SETTINGS)
		print(r'[Config file path]: {file_path}'.format(file_path=config_file_path))

		if not path_exists(config_file_path):
			raise Exception(
				r'[Error] Invalid config file path: {}'.format(config_file_path)
			)

		# 2. Parsing arguments
		parser = ArgumentParser(description=r'A Simple tool of Mysql tables tables checking.')
		parser.add_argument(
			'--cert_folder', required=True, default='', help='folder of ssl cert pem files.'
		)
		parser.add_argument(
			'--fr_mysql_pswd', default=None, help='Mysql pswd of French Nodes'
		)
		parser.add_argument(
			'--us_mysql_pswd', default=None, help='Mysql pswd of United States Nodes'
		)
		parser.add_argument(
			'--policy_name', required=True,
			choices=policy_manager.supported_policies,
			help='Pls, Specified a policy name'
		)
		args = parser.parse_args()
		if not path_exists(args.cert_folder):
			raise Exception(
				r'[Error] Invalid SSL Pem key folder: {}'.format(args.cert_folder)
			)
		if not args.fr_mysql_pswd and not args.us_mysql_pswd:
			raise Exception(
				r'[Error] Invalid MySql password of FR & US nodes: {} / {}'.format(
					args.fr_mysql_pswd, args.us_mysql_pswd
				)
			)

		# 3. Execute verification
		with Nodes(config_file_path, args.cert_folder) as ec2nodes:
			Verification(
				ec2nodes,
				args.fr_mysql_pswd,
				args.us_mysql_pswd,
				policy_manager.get_policy_obj_by_name(args.policy_name)
			).execute()

		print(r'[DONE]')

	except Exception:
		print(r'[Exception]: {err_msg}'.format(err_msg=format_exc()))
		process_terminate(10)
