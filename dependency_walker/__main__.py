"""
	A dependency walker program. Like: MS. `depends.exe`.

	Usage:
		root@24d914602ec3:/edx/app/edxapp/edx-platform# python -m dependency_walker --requirements="ci/requirements.aws.txt"

		[Exception]: Traceback (most recent call last):
		  File "/edx/src/dependency_walker/__main__.py", line 34, in <module>
			pkgr.require(requirements)
		  File "/edx/app/edxapp/venvs/edxapp/local/lib/python2.7/site-packages/pkg_resources/__init__.py", line 898, in require
			needed = self.resolve(parse_requirements(requirements))
		  File "/edx/app/edxapp/venvs/edxapp/local/lib/python2.7/site-packages/pkg_resources/__init__.py", line 789, in resolve
			raise VersionConflict(dist, req).with_context(dependent_req)
		VersionConflict: (six 1.11.0 (/edx/app/edxapp/venvs/edxapp/lib/python2.7/site-packages), Requirement.parse('six==1.12.0'))

"""

from argparse import ArgumentParser
from os.path import (
	exists as path_exists,
	isfile
)
import pkg_resources as pkgr
from sys import exit as process_terminate
from traceback import format_exc


if __name__ == "__main__":
	try:
		# Parsing arguments
		parser = ArgumentParser(description=r'A Simple tool of python dependency walker.')
		parser.add_argument(
			'--requirements', default='', help='path of requirements.txt'
		)
		args = parser.parse_args()
		if not path_exists(args.requirements) or not isfile(args.requirements):
			raise Exception(
				r'[Error] Invalid path of requirements.txt: {}'.format(args.requirements)
			)

		with open(args.requirements, 'r') as req_file:
			requirements = [
				r'{}{}'.format(py_lib.name, py_lib.specifier)
				for py_lib in pkgr.parse_requirements(req_file)
			]
			pkgr.require(requirements)

		print(r'[DONE]')

	except Exception:
		print(r'[Exception]: {err_msg}'.format(err_msg=format_exc()))
		process_terminate(10)
