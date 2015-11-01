
"""
	Patterns to make name and version formatting uniform.

	Use translation when it's available, silently do nothing otherwise.
"""

try:
	from django.utils.translation import ugettext_lazy as _
except ImportError:
	_ = lambda text: text


PACKAGE_NAME_PATTERN = r'[a-z][a-z0-9_]{0,31}'
PACKAGE_NAME_MESSAGE = _('Package names may contain up to 32 lowercase letters, numbers and underscores ' +
	'and must start with a letter.')

VERSION_REST_PATTERN = r'[^.][a-zA-Z0-9_\-.]+'
VERSION_PATTERN = r'\d{1,4}(?:\.\d{1,4}(?:\.' + VERSION_REST_PATTERN + ')?)$'
VERSION_MESSAGE = _('Version numbers should be formatted like 1.0.dev7, the first two being under 10,000.')

FILENAME_PATTERN = r'[a-zA-Z0-9_\-.]{1,32}'
FILENAME_MESSAGE = _('File and directory names may contain up to 32 alphanumeric characters, periods, ' + \
	'dashes and underscores.')
# the 32 is the chosen db limit


