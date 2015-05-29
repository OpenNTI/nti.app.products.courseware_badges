#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import os
import argparse

from nti.dataserver.users import User
from nti.dataserver.utils import run_with_dataserver
from nti.dataserver.utils.base_script import set_site
from nti.dataserver.utils.base_script import create_context

from .. import get_course_badges_for_user

def _process_args(args):
	if args.site:
		set_site(args.site)

	user = User.get_user(args.username)
	if user is None:
		raise ValueError("User cannot be found")

	badges = get_course_badges_for_user(user)
	for badge in badges:
		print(badge.name)

def main():
	arg_parser = argparse.ArgumentParser(description="User course badges")
	arg_parser.add_argument('username', help="The username")
	arg_parser.add_argument('-v', '--verbose', help="Be verbose", action='store_true',
							dest='verbose')
	arg_parser.add_argument('--site', dest='site',
							help="Application SITE.")
	args = arg_parser.parse_args()

	env_dir = os.getenv('DATASERVER_DIR')
	if not env_dir or not os.path.exists(env_dir) and not os.path.isdir(env_dir):
		raise IOError("Invalid dataserver environment root directory")

	context = create_context(env_dir)
	conf_packages = ('nti.appserver',)

	run_with_dataserver(environment_dir=env_dir,
						xmlconfig_packages=conf_packages,
						verbose=args.verbose,
						context=context,
						function=lambda: _process_args(args))

if __name__ == '__main__':
	main()
