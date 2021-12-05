"""
	The entry of module.

	export Mysql databases settings for Service course-discovery.


	Usage:

		Command: `python -m export_discovery_settings`

"""

from os import listdir
from os.path import (
	dirname as file_dirname,
	exists as path_exists,
	isfile,
	join as path_join
)
from sys import exit as process_terminate
from traceback import format_exc


from private_py_dumper import FilePrivatePyDumper


if __name__ == "__main__":
	try:
		SUBFOLDER_OF_CONFIGURATIONS = r'../../hawthorn/src/hawthorn_inventory/configuration_files'
		config_root = path_join(file_dirname(__file__), SUBFOLDER_OF_CONFIGURATIONS)
		print(r'[Root Folder]: {config_dir}'.format(config_dir=config_root))

		if not path_exists(config_root):
			raise Exception(
				r'[Error] Invalid config dir: {}'.format(config_root)
			)

		nodes_config_folders = [
			path_join(config_root, path_str)
			for path_str in listdir(config_root) if not isfile(path_str)
		]
		nodes_folders_count = len(nodes_config_folders)
		output_folder = path_join(file_dirname(__file__), r'output')
		print(r'[Node Folders Count]: {}'.format(nodes_folders_count))
		print(r'[Output Folder]: {}'.format(output_folder))

		for path_str in nodes_config_folders:
			FilePrivatePyDumper(path_str, output_folder).dump()

		print(r'[DONE]')

	except Exception:
		print(r'[Exception]: {err_msg}'.format(err_msg=format_exc()))
		process_terminate(10)
