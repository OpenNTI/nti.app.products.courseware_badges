#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

generation = 2

from .install import install_course_badge_cache

def do_evolve(context):
	install_course_badge_cache(context)

def evolve(context):
	"""
	Evolve to generation 2 by registering cache
	"""
	do_evolve(context)
