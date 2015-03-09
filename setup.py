#!/usr/bin/env python

import os, sys

from setuptools import setup, find_packages
from setuptools import Command


README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


class TestCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from django.conf import settings

        settings.configure(
            DATABASES = {
                'default': {
                    'NAME': ':memory:',
                    'ENGINE': 'django.db.backends.sqlite3'
                }
            },
            INSTALLED_APPS = (
                'floppyforms',
                'supasurvey',
            )
        )

        import django

        if django.VERSION[:2] >= (1, 7):
            from django.core.management import call_command
            django.setup()
            call_command('test', 'multifilefield')
        else:
            from supasurvey.runtests import runtests
            runtests()


setup(name='supasurvey',
    version='0.0.5',
    packages=find_packages(),
    include_package_data=True,
    license='BSD License',
    description='Some code for making some surveys :)',
    long_description=README,
    url='https://github.com/invisiblehands/django-supasurvey/',
    author_email='cody@invisiblehands.ca',
    author='Cody Redmond',
    install_requires=[
        'Django>=1.6.0',
        'jsonfield>=1.0.0',
        'django-floppyforms>=1.1.0'
    ],
    tests_require=[
        'Django>=1.6.0',
        'jsonfield>=1.0.0',
        'django-floppyforms>=1.1.0'
    ],
    cmdclass={'test': TestCommand},
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License'
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content'
    ],
)
