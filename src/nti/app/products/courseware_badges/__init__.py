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

def get_course_badges(ntiid, badge_types=course_badge_types):
	"""
	return all the course badges.

	The name a course badge is 'root' course NTIID plus a period (.) plus course_{type}_badge
	e.g tag:nextthought.com,2011-10:OU-HTML-CLC3403_LawAndJustice.course_completion_badge
	that is the completion badge of the tag:nextthought.com,2011-10:OU-HTML-CLC3403_LawAndJustice
 	course
 	"""
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
