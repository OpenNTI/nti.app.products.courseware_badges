#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
.. $Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import os
import re

from nti.badges.openbadges import interfaces as open_interfaces

from nti.ntiids import ntiids

from . import interfaces

def base_root_ntiid(ntiid):
	"""
	return the 'root' ntiid of a source ntiid. That is, we remove from the NTIID-source
	specific part anything after the first period (.)  so from
	tag:nextthought.com,2011-10:OU-HTML-CLC3403_LawAndJustice.clc_3403_law_and_justice
	we get tag:nextthought.com,2011-10:OU-HTML-CLC3403_LawAndJustice
	"""
	parts = ntiids.get_parts(ntiid)
	specfic = parts.specific.split('.')[0]
	result = ntiids.make_ntiid(provider=parts.provider,
							   nttype=parts.nttype,
							   specific=specfic,
							   base=parts.date)
	return result

def get_base_image_filename(badge):
	"""
	return the image file name w/ no ext
	"""
	image = open_interfaces.IBadgeClass(badge).image
	filename = os.path.basename(image) if image else None
	if filename and filename.lower().endswith('.png'):
		filename = os.path.splitext(filename)[0]
	return filename

type_pattern = re.compile("course_(.+)_badge", re.I | re.U)
def get_badge_type_from_filename(filename):
	m = type_pattern.match(filename)
	if m is not None:
		result = m.groups()[0].lower()
	else:
		result = interfaces.COURSE_COMPLETION
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

def find_course_badge_from_badges(course_ntiid, source_badges=()):
	"""
	return all the badges for the specified course using the badge image names

	The image file name of a course badge is 'root' course NTIID plus a period (.) plus course_{type}_badge
	e.g tag_nextthought.com_2011-10_OU-HTML-CLC3403_LawAndJustice.course_completion_badge.png
	that is the completion badge of the tag:nextthought.com,2011-10:OU-HTML-CLC3403_LawAndJustice
 	course
 	"""
	badge_types = interfaces.COURSE_BADGE_TYPES
	badge_types = ['course_%s_badge' % x for x in badge_types] + ['course_badge']

	badge_type_ntiids = set()
	parts = ntiids.get_parts(course_ntiid)
	pre_specfic = '.'.join(parts.specific.split('.')[0:-1]) or parts.specific
	for subtype in badge_types:
		specfic = '%s.%s' % (pre_specfic, subtype)
		name = ntiids.make_ntiid(provider=parts.provider,
								 nttype=parts.nttype,
								 specific=specfic,
								 base=parts.date)
		badge_type_ntiids.add(name.replace(':', '_').replace(',', '_'))

	result = []
	for badge in source_badges:
		possible_ntiid = get_base_image_filename(badge)
		if possible_ntiid in badge_type_ntiids:
			result.append(badge)
	return result
