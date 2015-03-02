#!/usr/bin/env python

import sys

from django.conf import settings


def runtests():
    from django.test.utils import get_runner

    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=1, interactive=True)

    failures = test_runner.run_tests(['supasurvey'])
    sys.exit(bool(failures))


if __name__ == '__main__':
    runtests()

