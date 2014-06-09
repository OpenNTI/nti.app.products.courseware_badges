#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

import os
import shutil
import tempfile

from zope import component
from zope.component.interfaces import IComponents

import ZODB

from nti.app.products.courseware.interfaces import ICourseCatalog

from nti.badges.tahrir import manager
from nti.badges import interfaces as badge_interfaces

from nti.contentlibrary.interfaces import IContentPackageLibrary

from nti.dataserver import users

from nti.app.products.courseware_badges.tests.badges import generate_db

from nti.dataserver.tests.mock_dataserver import WithMockDS
from nti.dataserver.tests.mock_dataserver import mock_db_trans

from nti.app.testing.application_webtest import ApplicationTestLayer

from nti.testing.layers import find_test
from nti.testing.layers import GCLayerMixin
from nti.testing.layers import ZopeComponentLayer
from nti.testing.layers import ConfiguringLayerMixin

from nti.dataserver.tests.mock_dataserver import DSInjectorMixin

import zope.testing.cleanup

def _change_ds_dir(cls):
    cls.old_data_dir = os.getenv('DATASERVER_DATA_DIR')
    cls.new_data_dir = tempfile.mkdtemp(dir="/tmp")
    os.environ['DATASERVER_DATA_DIR'] = cls.new_data_dir

def _restore_ds_dir(cls):
    shutil.rmtree(cls.new_data_dir, True)
    os.environ['DATASERVER_DATA_DIR'] = cls.old_data_dir or '/tmp'

def _register_sample(cls):
    import transaction
    with transaction.manager:
        cls.old = component.getUtility(badge_interfaces.IBadgeManager)
        bm = manager.create_badge_manager(defaultSQLite=True)
        generate_db(bm.db)
        component.provideUtility(bm, badge_interfaces.IBadgeManager)

def _do_then_enumerate_library(do):
    database = ZODB.DB(ApplicationTestLayer._storage_base, database_name='Users')

    @WithMockDS(database=database)
    def _create():
        with mock_db_trans():
            do()

            lib = component.getUtility(IContentPackageLibrary)
            try:
                del lib.contentPackages
            except AttributeError:
                pass

            getattr(lib, 'contentPackages')

            components = component.getUtility(IComponents, name='platform.ou.edu')
            catalog = components.getUtility(ICourseCatalog)

            # re-register globally
            global_catalog = component.getUtility(ICourseCatalog)
            global_catalog._entries[:] = catalog._entries

    _create()

class SharedConfiguringTestLayer(ZopeComponentLayer,
                                 GCLayerMixin,
                                 ConfiguringLayerMixin,
                                 DSInjectorMixin):

    _library_path = 'Library'

    set_up_packages = ('nti.dataserver',
                       'nti.app.client_preferences',
                       'nti.app.products.courseware_badges')

    @classmethod
    def setUp(cls):
        cls.setUpPackages()
        _change_ds_dir(cls)
        _register_sample(cls)

    @classmethod
    def tearDown(cls):
        cls.tearDownPackages()
        zope.testing.cleanup.cleanUp()
        _restore_ds_dir(cls)

    @classmethod
    def testSetUp(cls, test=None):
        cls.setUpTestDS(test)
        
    @classmethod
    def testTearDown(cls):
        pass

import unittest

class CourseBadgesTestCase(unittest.TestCase):
    layer = SharedConfiguringTestLayer

class CourseBadgesApplicationTestLayer(ApplicationTestLayer):

    _library_path = 'Library'

    @classmethod
    def _setup_library(cls, *args, **kwargs):
        from nti.contentlibrary.filesystem import CachedNotifyingStaticFilesystemLibrary as Library
        lib = Library(
            paths=(
                os.path.join(
                    os.path.dirname(__file__),
                    cls._library_path,
                    'CLC3403_LawAndJustice'),))
        return lib

    @classmethod
    def setUp(cls):
        _change_ds_dir(cls)
        _register_sample(cls)
        # Must implement!
        cls.__old_library = component.getUtility(IContentPackageLibrary)
        component.provideUtility(cls._setup_library(), IContentPackageLibrary)
        _do_then_enumerate_library(lambda: users.User.create_user(username='harp4162', password='temp001'))

    @classmethod
    def tearDown(cls):
        _restore_ds_dir(cls)
        # Clean up any side effects of these content packages being
        # registered
        def cleanup():
            del component.getUtility(IContentPackageLibrary).contentPackages
            try:
                del cls.__old_library.contentPackages
            except AttributeError:
                pass
            component.provideUtility(cls.__old_library, IContentPackageLibrary)

        _do_then_enumerate_library(cleanup)
        del cls.__old_library
