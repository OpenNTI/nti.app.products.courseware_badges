#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import component
from zope import interface

from nti.contenttypes.courses.interfaces import ICourseCatalog
from nti.contenttypes.courses.interfaces import ICourseInstance
from nti.contenttypes.courses.interfaces import ICourseCatalogEntry

from nti.badges.interfaces import IBadgeClass

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
		for entry in catalog.iterCatalogEntries():
			# collecct all possible matching ntiids
			ntiids = { getattr(entry,'ntiid', None) }
			course = ICourseInstance(entry, None)
			if course is not None:
				# for legacy badges get the ntiids of the content packages
				try:
					bundle = course.ContentPackageBundle
					ntiids.add(getattr(bundle, 'ntiid', None))
					ntiids.add(getattr(bundle, 'ContentPackageNTIID', None))
					for pack in bundle.ContentPackages:
						ntiids.add(pack.ntiid)
				except AttributeError: # in case no ContentPackageBundle
					pass
	
			ntiids.discard(None)	
			for ntiid in ntiids:
				if ntiid and _compare_pseudo_ntiids(ntiid_root, base_root_ntiid(ntiid)):
					return entry
	return None

@component.adapter(IBadgeClass)
@interface.implementer(ICourseCatalogEntry)
def badge_to_course_catalog_entry(badge):
	result = find_catalog_entry_from_badge(badge)
	return result
