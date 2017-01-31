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

from ZODB.POSException import POSError

from pyramid.threadlocal import get_current_request

from nti.app.products.badges.interfaces import IAssertionChange

from nti.app.products.courseware_badges import show_course_badges

from nti.app.products.courseware_badges.courses import is_course_badge

from nti.appserver.interfaces import IPrincipalUGDFilter

from nti.badges.interfaces import IBadgeClass

from nti.dataserver.interfaces import IUser


@component.adapter(IUser)
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
                user = IUser(assertion)
                badge = IBadgeClass(assertion)
                if req.authenticated_userid != user.username:
                    result =   not is_course_badge( badge.name) \
                            or show_course_badges(user)
            except (POSError, TypeError):
                result = False
        return result
