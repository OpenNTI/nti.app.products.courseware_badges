#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from pyramid.view import view_config

from nti.app.base.abstract_views import AbstractAuthenticatedView

from nti.badges import interfaces as badge_interfaces

from nti.contenttypes.courses.interfaces import ICourseInstance

from nti.dataserver import authorization as nauth

from nti.externalization.interfaces import LocatedExternalDict

from . import VIEW_BADGES
from . import get_course_badges

@view_config(route_name='objects.generic.traversal',
              context=ICourseInstance,
              request_method='GET',
              permission=nauth.ACT_READ,
              renderer='rest',
              name=VIEW_BADGES)
class CourseBadgesView(AbstractAuthenticatedView):

    def __call__(self):
        result = LocatedExternalDict()
        result['Items'] = items = []
        content_package_ntiid = getattr(self.request.context, 'ContentPackageNTIID', None)
        if content_package_ntiid:
            badges = get_course_badges(content_package_ntiid)
            items.extend(badge_interfaces.INTIBadge(b) for b in badges)
        result.__name__ = self.request.view_name
        result.__parent__ = self.request.context
        self.request.response.last_modified = self.request.context.lastModified
        return result

