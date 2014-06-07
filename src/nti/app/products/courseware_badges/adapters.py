#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
.. $Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import component
from zope import interface

from nti.app.products.courseware.interfaces import ICourseCatalogEntry

from nti.badges import interfaces as badge_interfaces

from nti.contentlibrary import interfaces as lib_interfaces

from nti.contenttypes.courses.interfaces import ICourseInstance

from . import base_root_ntiid
from . import get_base_image_filename
from . import is_course_badge_filename

@component.adapter(badge_interfaces.IBadgeClass)
@interface.implementer(lib_interfaces.IContentPackage)
def badge_to_course_content_package(badge):
	filename = get_base_image_filename(badge)
	if is_course_badge_filename(filename):
		# remove subtype from NTIID, filename is not a valid NTIID
		proxied_ntiid = '.'.join(filename.split('.')[0:-1])
		# replace ':',',' to before comparing
		proxied_ntiid = proxied_ntiid.replace(':', '_').replace(',', '_')
		# search packages
		library = component.queryUtility(lib_interfaces.IContentPackageLibrary)
		for package in getattr(library, 'contentPackages', ()):
			root_package_nttid = base_root_ntiid(package.ntiid)
			root_package_nttid = root_package_nttid.replace(':', '_').replace(',', '_')
			if proxied_ntiid == root_package_nttid:
				return package
	return None

@component.adapter(badge_interfaces.IBadgeClass)
@interface.implementer(ICourseCatalogEntry)
def badge_to_course_catalog_entry(badge):
	unit = lib_interfaces.IContentPackage(badge, None)
	course = ICourseInstance(unit, None)
	entry = ICourseCatalogEntry(course, None)
	return entry
