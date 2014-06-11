#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
.. $Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import six
import simplejson

from zope import component
from zope.lifecycleevent import IObjectAddedEvent

from nti.contentlibrary.interfaces import ILegacyCourseConflatedContentPackage

from . import interfaces

@component.adapter(ILegacyCourseConflatedContentPackage, IObjectAddedEvent)
def _content_package_registered(package, event):
	if not package.courseInfoSrc:
		return

	info_json_string = package.read_contents_of_sibling_entry(package.courseInfoSrc)
	if not info_json_string:
		return

	info_json_string = unicode(info_json_string, 'utf-8')
	info_json_dict = simplejson.loads(info_json_string)

	ntiid = package.ntiid
	badge_map = component.getUtility(interfaces.ICourseBadgeMap)
	badges = info_json_dict.get('badges') or info_json_dict.get('badge') or {}
	if isinstance(badges, six.string_types):
		badges = {badges:interfaces.COURSE_COMPLETION}
	
	for name, kind in badges.items():
		kind = kind or interfaces.COURSE_COMPLETION
		badge_map.add(ntiid, name, kind)
