#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import os
import re
import six
from collections import Mapping

from zope import component
from zope.traversing.api import traverse

from pyramid.compat import is_nonstr_iter

from nti.badges.openbadges.interfaces import IBadgeClass

from nti.contenttypes.courses.interfaces import ICourseCatalog
from nti.contenttypes.courses.interfaces import ICourseInstance
from nti.contenttypes.courses.interfaces import ICourseInstanceVendorInfo

from nti.ntiids import ntiids

from .interfaces import COURSE_COMPLETION
from .interfaces import COURSE_BADGE_TYPES

ROOT = "tag:nextthought.com,2011-10:"
SAFE_ROOT = ROOT.replace(':', '_').replace(',', '_')

def base_root_ntiid(ntiid):
	"""
	return the 'root' ntiid of a source ntiid. That is, we remove from the NTIID-source
	specific part anything after the first period (.)  so from
	tag:nextthought.com,2011-10:OU-HTML-CLC3403_LawAndJustice.clc_3403_law_and_justice
	we get tag:nextthought.com,2011-10:OU-HTML-CLC3403_LawAndJustice
	"""
	if ntiid and ntiids.is_valid_ntiid_string(ntiid):
		parts = ntiids.get_parts(ntiid)
		specfic = parts.specific.split('.')[0]
		result = ntiids.make_ntiid(provider=parts.provider,
								   nttype=parts.nttype,
								   specific=specfic,
								   base=parts.date)
		return result
	return None

def get_base_image_filename(badge):
	"""
	return the image file name w/ no ext
	"""
	image = IBadgeClass(badge).image
	filename = os.path.basename(image) if image else None
	if filename and filename.lower().endswith('.png'):
		filename = os.path.splitext(filename)[0]
		if not filename.startswith(SAFE_ROOT):
			filename = SAFE_ROOT + filename
	return filename

type_pattern = re.compile("course_(.+)_badge", re.I | re.U)
def get_badge_type_from_filename(filename):
	m = type_pattern.match(filename)
	if m is not None:
		result = m.groups()[0].lower()
	else:
		result = COURSE_COMPLETION
	return result

def get_badge_type(badge):
	filename = get_base_image_filename(badge)
	result = get_badge_type_from_filename(filename)
	return result

filename_pattern = re.compile("(.+\.course_.+_badge$)|(.+\.course_badge$)", re.I | re.U)
def is_course_badge_filename(filename):
	result = filename_pattern.match(filename) if filename else None
	return True if result else False

def is_course_badge(badge):
	filename = get_base_image_filename(badge)
	result = is_course_badge_filename(filename)
	return result

_all_badge_types = tuple(['course_%s_badge' % x for x in COURSE_BADGE_TYPES] + ['course_badge'])

def find_course_badges_from_entry(context):
	course = ICourseInstance(context, None)
	vendor_info = ICourseInstanceVendorInfo(course, {})
	result = traverse(vendor_info, 'NTI/Badges', default=None)
	return result

def find_course_badges_from_badges(source_ntiid, source_badges=()):
	"""
	return all the badges for the specified course using the badge image names

	The image file name of a course badge is 'root' course/content pagckage NTIID plus
	a period (.) plus course_{type}_badge
	e.g tag_nextthought.com_2011-10_OU-HTML-CLC3403_LawAndJustice.course_completion_badge.png
	that is the completion badge of the tag:nextthought.com,2011-10:OU-HTML-CLC3403_LawAndJustice
 	course
 	"""

	if not ntiids.is_valid_ntiid_string(source_ntiid):
		raise ValueError("Invalid course ntiid")

	result = []
	badge_type_ntiids = set()
	catalog = component.queryUtility(ICourseCatalog)
	if catalog:
		try:
			entry = catalog.getCatalogEntry(source_ntiid)
			badges = find_course_badges_from_entry(entry)
			if isinstance(badges, Mapping):
				badge_type_ntiids.update(badges.keys())
			elif is_nonstr_iter(badges):
				badge_type_ntiids.update(badges)
			elif isinstance(badges, six.string_types):
				badge_type_ntiids.add(badges)
				
			## make sure the badge ids in vendor-info are valid
			for badge in source_badges:
				ntiid = get_base_image_filename(badge)
				if badge.name in badge_type_ntiids or ntiid in badge_type_ntiids:
					result.append(CourseBadgeProxy(badge, source_ntiid))
			
			if result:
				return result
		except KeyError:
			pass
		
	## Could not find badges in vendor info
	## build possible ntiids basod in the course entry ntiid
	badge_type_ntiids.clear()
	parts = ntiids.get_parts(source_ntiid)
	pre_specfic = '.'.join(parts.specific.split('.')[0:-1]) or parts.specific
	for subtype in _all_badge_types:
		specfic = '%s.%s' % (pre_specfic, subtype)
		name = ntiids.make_ntiid(provider=parts.provider,
								 nttype=parts.nttype,
								 specific=specfic,
								 base=parts.date)
		badge_type_ntiids.add(name.replace(':', '_').replace(',', '_'))

	## check built ntiids against badge file name(s)
	for badge in source_badges:
		ntiid = get_base_image_filename(badge)
		if ntiid in badge_type_ntiids:
			result.append(CourseBadgeProxy(badge, source_ntiid))

	return result

from zope.proxy import ProxyBase

class CourseBadgeProxy(ProxyBase):
	
	SourceNTIID = property(
			lambda s: s.__dict__.get('_v_catalog_source_ntiid'),
			lambda s, v: s.__dict__.__setitem__('_v_catalog_source_ntiid', v))
		
	def __new__(cls, base, ntiid):
		return ProxyBase.__new__(cls, base)

	def __init__(self, base, ntiid):
		ProxyBase.__init__(self, base)
		self.SourceNTIID = ntiid
