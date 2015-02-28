#!/usr/bin/env python

from setuptools import setup
from setuptools import Command


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
            INSTALLED_APPS = ('floppyforms', 'supasurvey',)
        )

        from django.core.management import call_command
        import django

        if django.VERSION[:2] >= (1, 7):
            django.setup()

        call_command('test', 'supasurvey')


setup(name='supasurvey',
    version='0.0.1',
    packages=['supasurvey'],
    license='MIT',
    author='Cody Redmond',
    author_email='cody@invisiblehands.ca',
    url='https://github.com/invisiblehands/django-supasurvey/',
    description='Some code for making some surveys :)',
    long_description=open('README.md').read(),
    install_requires=[
        'Django>=1.6.0',
        'jsonfield>=1.0.0',
        'django-floppyforms>=1.2.0'
    ],
    tests_require=[
        'Django>=1.6.0',
        'jsonfield>=1.0.0',
        'django-floppyforms>=1.2.0'
    ],
    cmdclass={'test': TestCommand},
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Framework :: Django',
    ],
)
