# Amara, universalsubtitles.org
#
# Copyright (C) 2012 Participatory Culture Foundation
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see
# http://www.gnu.org/licenses/agpl-3.0.html.

from settings import *
from dev_settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': "/tmp/django_test_db.sqlite",
        'USER': "",
        'PASSWORD': "",
        'HOST': "",
        'PORT': ''
        }
    }

CACHE_PREFIX = "testcache"
CACHE_TIMEOUT = 60
DEFAULT_PROTOCOL = 'https'
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
CELERY_ALWAYS_EAGER = True

import logging
logging.getLogger('pysolr').setLevel(logging.ERROR)

try:
    from dev_settings_test_local import *
except ImportError:
    pass
