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

from zope.proxy import ProxyBase

from zope.traversing.api import traverse

from pyramid.compat import is_nonstr_iter

from nti.app.products.courseware_badges.interfaces import COURSE_COMPLETION
from nti.app.products.courseware_badges.interfaces import COURSE_BADGE_TYPES

from nti.badges.openbadges.interfaces import IBadgeClass

from nti.contenttypes.courses import get_course_vendor_info

from nti.contenttypes.courses.interfaces import ICourseCatalog
from nti.contenttypes.courses.interfaces import ICourseInstance
from nti.contenttypes.courses.interfaces import ICourseCatalogEntry

from nti.ntiids.ntiids import get_parts
from nti.ntiids.ntiids import make_ntiid
from nti.ntiids.ntiids import is_valid_ntiid_string
from nti.ntiids.ntiids import find_object_with_ntiid

ROOT = "tag:nextthought.com,2011-10:"
SAFE_ROOT = ROOT.replace(':', '_').replace(',', '_')

def base_root_ntiid(ntiid):
	"""
	return the 'root' ntiid of a source ntiid. That is, we remove from the NTIID-source
	specific part anything after the first period (.)  so from
	tag:nextthought.com,2011-10:OU-HTML-CLC3403_LawAndJustice.clc_3403_law_and_justice
	we get tag:nextthought.com,2011-10:OU-HTML-CLC3403_LawAndJustice
	"""
	if ntiid and is_valid_ntiid_string(ntiid):
		parts = get_parts(ntiid)
		specfic = parts.specific.split('.')[0]
		result = make_ntiid(provider=parts.provider,
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
	vendor_info = get_course_vendor_info(course, False) or {}
	result = traverse(vendor_info, 'NTI/Badges', default=None)
	return result

class CourseBadgeProxy(ProxyBase):

	SourceNTIID = property(
			lambda s: s.__dict__.get('_v_catalog_source_ntiid'),
			lambda s, v: s.__dict__.__setitem__('_v_catalog_source_ntiid', v))

	def __new__(cls, base, ntiid):
		return ProxyBase.__new__(cls, base)

	def __init__(self, base, ntiid):
		ProxyBase.__init__(self, base)
		self.SourceNTIID = ntiid

def proxy(badge, ntiid):
	return CourseBadgeProxy(badge, ntiid)

def catalog_entry(context):
	if not ICourseCatalogEntry.providedBy(context):
		context = ICourseCatalogEntry(context, None)
	return context

def find_catalog_entry(iden):
	catalog = component.queryUtility(ICourseCatalog)
	if catalog is not None:
		try:
			entry = catalog.getCatalogEntry(iden)
		except KeyError:
			entry = find_object_with_ntiid(iden) if is_valid_ntiid_string(iden) else None
		entry = catalog_entry(entry)
		return entry
	return None

def find_course_badges_from_badges(source_ntiid, source_badges=()):
	"""
	return all course badges from the specified badge source iterable

	if the source_ntiid is a catalog entry ntiid, we look at the course
	vendor info (e.g. NTI/Badges) to find the badge names. otherwise
	we use the badge image file names to determined a course badge.
	The image file name of a course badge is 'root' course/content package NTIID plus
	a period (.) plus course_{type}_badge
	e.g tag_nextthought.com_2011-10_OU-HTML-CLC3403_LawAndJustice.course_completion_badge.png
	that is the completion badge of the tag:nextthought.com,2011-10:OU-HTML-CLC3403_LawAndJustice
 	course
 	"""

	result = []
	badge_ntiids = set()
	entry = find_catalog_entry(source_ntiid)
	if entry is not None:
		badges = find_course_badges_from_entry(entry)
		if isinstance(badges, Mapping):
			# keys of the map are the badge names
			# the values are the badge types
			badge_ntiids.update(badges.keys())
		elif is_nonstr_iter(badges):
			# the iterable contains the badge names
			badge_ntiids.update(badges)
		elif isinstance(badges, six.string_types):
			# a single string it's the badge name
			badge_ntiids.add(badges)

		# make sure the badge ids in vendor-info are valid
		for badge in source_badges:
			ntiid = get_base_image_filename(badge)
			if badge.name in badge_ntiids or ntiid in badge_ntiids:
				result.append(proxy(badge, source_ntiid))
		if result:
			return result

	if not is_valid_ntiid_string(source_ntiid):
		return result

	# Could not find badges in vendor info
	# build possible ntiids based in the course entry ntiid
	badge_ntiids.clear()
	parts = get_parts(source_ntiid)
	pre_specfic = '.'.join(parts.specific.split('.')[0:-1]) or parts.specific
	for subtype in _all_badge_types:
		specfic = '%s.%s' % (pre_specfic, subtype)
		name = make_ntiid(provider=parts.provider,
						  nttype=parts.nttype,
						  specific=specfic,
						  base=parts.date)
		badge_ntiids.add(name.replace(':', '_').replace(',', '_'))

	# check built ntiids against badge file name(s)
	for badge in source_badges:
		ntiid = get_base_image_filename(badge)
		if ntiid in badge_ntiids:
			result.append(proxy(badge, source_ntiid))
	return result
