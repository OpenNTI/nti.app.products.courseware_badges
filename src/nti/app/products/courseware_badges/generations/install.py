#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from zope.generations.generations import SchemaManager

from zope.intid.interfaces import IIntIds

from nti.app.products.courseware_badges.index import install_course_badges_catalog

generation = 5

logger = __import__('logging').getLogger(__name__)


class _CoursewareBadgesSchemaManager(SchemaManager):
    """
    A schema manager that we can register as a utility in ZCML.
    """

    def __init__(self):
        super(_CoursewareBadgesSchemaManager, self).__init__(
            generation=generation,
            minimum_generation=generation,
            package_name='nti.app.products.courseware_badges.generations')


def install_catalog(context):
    pass


def evolve(context):
    pass
