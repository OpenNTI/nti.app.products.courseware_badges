#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
.. $Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import os

from zope import component
from zope import interface

from nti.badges import interfaces as badge_interfaces
from nti.badges.openbadges import interfaces as open_interfaces

from nti.contentlibrary import interfaces as lib_interfaces

from . import is_course_badge
from . import base_root_ntiid

@component.adapter(badge_interfaces.IBadgeClass)
@interface.implementer(lib_interfaces.IContentPackage)
def badge_to_course_content_package(badge):
	if is_course_badge(badge):
		image = open_interfaces.IBadgeClass(badge).image
		filename = os.path.basename(image)
		filename = os.path.splitext(filename)[0]  # file name no extention
		badge_ntiid = '.'.join(filename.split('.'))[0:-1]  # not a valid nttid
		badge_ntiid = badge_ntiid.replace(':', '_').replace(',', '_') # should be a root ntiid

		library = component.queryUtility(lib_interfaces.IContentPackageLibrary)
		for package in getattr(library, 'contentPackages', ()):
			root_package_nttid = base_root_ntiid(package.ntiid)
			root_package_nttid = root_package_nttid.replace(':', '_').replace(',', '_')
			if badge_ntiid == root_package_nttid:
				return package
	return None
