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


	Another Way:
		root@24d914602ec3:/edx/app/edxapp/edx-platform# pip check cryptography==3.3.2
			==> slackclient 1.3.2 has requirement requests<3.0a0,>=2.11, but you have requests 2.9.1.
			==> cryptography 3.3.2 has requirement cffi>=1.12, but you have cffi 1.11.5.

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
		parser.add_argument(
			'--blacklist', default='argparse', help='blacklist of excluding libraries (separated by comma)'
		)
		args = parser.parse_args()
		if not path_exists(args.requirements) or not isfile(args.requirements):
			raise Exception(
				r'[Error] Invalid path of requirements.txt: {}'.format(args.requirements)
			)

		print('[PROCESSING] message would be ignored if string `-e ` or `git+https:` exist in message.')
		with open(args.requirements, 'r') as req_file:
			libraries = filter(
				lambda line: '-e ' not in line and 'git+https:' not in line,
				iter(pkgr.yield_lines(req_file))
			)

			blacklist = args.blacklist.split(',')
			requirements = [
				r'{}{}'.format(py_lib.name, py_lib.specifier)
				for py_lib in pkgr.parse_requirements(libraries)
				if py_lib.name not in blacklist
			]

			pkgr.require(requirements)

		print(r'[DONE]')

	except Exception:
		print(r'[Exception]: {err_msg}'.format(err_msg=format_exc()))
		process_terminate(10)
