#!/usr/bin/env python
#
from distutils.core import setup
from distutils.core import Command


class TestCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from django.conf import settings
        settings.configure(DATABASES={'default': {'NAME': ':memory:',
            'ENGINE': 'django.db.backends.sqlite3'}},
            INSTALLED_APPS=('supasurvey',))
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
    long_description=open("README.md").read(),
    install_requires=['Django >= 1.6.0'],
    tests_require=['Django >= 1.6.0'],
    cmdclass={'test': TestCommand},
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Framework :: Django',
    ],
)