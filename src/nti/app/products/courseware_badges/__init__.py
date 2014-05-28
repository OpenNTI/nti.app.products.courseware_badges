#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
.. $Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import component

from nti.app.products.badges import get_badge

from nti.ntiids import ntiids

VIEW_BADGES = 'Badges'

course_completion_badge = u'course_completion_badge'
course_badge_types = (course_completion_badge,)

def get_course_badges(ntiid, badge_types=course_badge_types):
	result = []
	parts = ntiids.get_parts(ntiid)
	pre_specfic = '.'.join(parts.specific.split('.')[0:-1]) or parts.specific
	for subtype in badge_types:
		specfic = '%s.%s' % (pre_specfic, subtype)
		name = ntiids.make_ntiid(provider=parts.provider,
								 nttype=parts.nttype,
								 specific=specfic,
								 base=parts.date)
		badge = get_badge(name)
		if badge is not None:
			result.append(badge)
	return result

def get_course_completion_badge(ntiid):
	result = get_course_badges(ntiid, (course_completion_badge,))
	return result[0] if result else None
