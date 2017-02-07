import codecs
from setuptools import setup, find_packages

VERSION = '0.0.0'

entry_points = {
    'console_scripts': [
        "nti_user_course_badges = nti.app.products.courseware_badges.scripts.nti_user_course_badges:main",
    ],
    "z3c.autoinclude.plugin": [
        'target = nti.app.products',
    ],
}

setup(
    name='nti.app.products.courseware_badges',
    version=VERSION,
    author='Jason Madden',
    author_email='jason@nextthought.com',
    description="NTI Course Badges Product Integration",
    long_description=codecs.open('README.rst', encoding='utf-8').read(),
    license='Proprietary',
    keywords='Pyramid Preference',
    classifiers=[
        'Framework :: Pyramid',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython'
    ],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['nti', 'nti.app', 'nti.app.products'],
    install_requires=[
        'setuptools',
        'nti.app.products.badges',
        'nti.app.products.courseware'
    ],
    entry_points=entry_points
)
