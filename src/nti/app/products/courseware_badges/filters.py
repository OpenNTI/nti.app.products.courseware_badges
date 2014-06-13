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

from ZODB.POSException import POSKeyError

from pyramid.threadlocal import get_current_request

from nti.badges import interfaces as badge_interfaces

from nti.dataserver import interfaces as nti_interfaces

from nti.appserver.interfaces import IPrincipalUGDFilter

from nti.app.products.badges.interfaces import IAssertionChange

from . import show_course_badges
from . import get_catalog_entry_for_badge

@component.adapter(nti_interfaces.IUser)
@interface.implementer(IPrincipalUGDFilter)
class _CourseBadgePrincipalUGDFilter(object):

	def __init__(self, *args):
		pass

	def __call__(self, user, obj):
		result = True
		req = get_current_request()
		if req is not None and IAssertionChange.providedBy(obj):
			try:
				assertion = obj.object
				user = nti_interfaces.IUser(assertion)
				badge = badge_interfaces.IBadgeClass(assertion)
				if req.authenticated_userid != user.username:
					result = get_catalog_entry_for_badge(badge) is None or \
							 show_course_badges(user)
			except (POSKeyError, TypeError):
				result = False
		return result
		
