import codecs
from setuptools import setup, find_packages

entry_points = {
    'console_scripts': [
        "nti_user_course_badges = nti.app.products.courseware_badges.scripts.nti_user_course_badges:main",
    ],
    "z3c.autoinclude.plugin": [
        'target = nti.app.products',
    ],
}


TESTS_REQUIRE = [
    'nti.app.testing',
    'nti.testing',
    'zope.testrunner',
]


def _read(fname):
    with codecs.open(fname, encoding='utf-8') as f:
        return f.read()


setup(
    name='nti.app.products.courseware_badges',
    version=_read('version.txt').strip(),
    author='Jason Madden',
    author_email='jason@nextthought.com',
    description="NTI Course Badges Product Integration",
    long_description=(_read('README.rst') + '\n\n' + _read("CHANGES.rst")),
    license='Apache',
    keywords='pyramid course badges',
    classifiers=[
        'Framework :: Pyramid',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    url="https://github.com/NextThought/nti.app.products.courseware_badges",
    zip_safe=True,
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    namespace_packages=['nti', 'nti.app', 'nti.app.products'],
    tests_require=TESTS_REQUIRE,
    install_requires=[
        'setuptools',
        'nti.app.client_preferences',
        'nti.app.products.badges',
        'nti.app.products.courseware',
        'nti.badges',
        'nti.base',
        'nti.containers',
        'nti.contentlibrary',
        'nti.contenttypes.courses',
        'nti.externalization',
        'nti.links',
        'nti.ntiids',
        'nti.schema',
        'nti.site',
        'nti.zope_catalog',
        'pyramid',
        'requests',
        'six',
        'ZODB',
        'zope.cachedescriptors',
        'zope.catalog',
        'zope.component',
        'zope.container',
        'zope.deprecation',
        'zope.generations',
        'zope.intid',
        'zope.interface',
        'zope.location',
        'zope.preference',
        'zope.proxy',
        'zope.schema',
        'zope.security',
        'zope.traversing',
    ],
    extras_require={
        'test': TESTS_REQUIRE,
        'docs': [
            'Sphinx',
            'repoze.sphinx.autointerface',
            'sphinx_rtd_theme',
        ],
    },
    entry_points=entry_points,
)
