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

from nti.app.products.courseware.interfaces import ICourseCatalog
from nti.app.products.courseware.interfaces import ICourseCatalogEntry

from nti.badges import interfaces as badge_interfaces

from . import interfaces

from .utils import get_badge_type
from .utils import base_root_ntiid
from .utils import get_base_image_filename
from .utils import is_course_badge_filename

def _compare_pseudo_ntiids(a, b):
	if a and b:
		a_trx = a.replace(':', '_').replace(',', '_')
		b_trx = b.replace(':', '_').replace(',', '_')
		return a_trx == b_trx
	return False

def find_catalog_entry_from_badge(badge):
	filename = get_base_image_filename(badge)
	if is_course_badge_filename(filename):
		# remove subtype from NTIID, filename is not a valid NTIID
		ntiid_root = '.'.join(filename.split('.')[0:-1])
		# search catalog entries
		catalog = component.getUtility(ICourseCatalog)
		for entry in catalog:
			# TODO: ContentPackageNTIID will be deprecated
			unique_id = getattr(entry, 'ProviderUniqueID', None)
			pack_ntiid = getattr(entry, 'ContentPackageNTIID', None)
			if 	_compare_pseudo_ntiids(ntiid_root, base_root_ntiid(unique_id)) or \
				_compare_pseudo_ntiids(ntiid_root, base_root_ntiid(pack_ntiid)):
				return entry
	return None

@component.adapter(badge_interfaces.IBadgeClass)
@interface.implementer(ICourseCatalogEntry)
def badge_to_course_catalog_entry(badge):
	badge_name = badge.name
	badge_map = component.getUtility(interfaces.ICourseBadgeMap)
	course_iden = badge_map.get_course_iden(badge_name)
	if badge_map.is_no_course(course_iden):
		entry = None
	elif course_iden is None:
		entry = find_catalog_entry_from_badge(badge)
		if entry is not None:
			# populate badge map
			kind = get_badge_type(badge)
			course_iden = entry.ProviderUniqueID
			badge_map.add(course_iden, badge_name, kind)
		else:
			badge_map.mark_no_course(badge_name)
	else:
		catalog = component.getUtility(ICourseCatalog)
		try:
			entry = catalog[course_iden]
		except KeyError:
			entry = None
	return entry
