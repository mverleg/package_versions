
"""
	Patterns to make name and version formatting uniform.

	Use translation when it's available, silently do nothing otherwise.

	* A length is chosen to be able to use database charfields;
		32 seemed reasonable and Python encourages short module names.
	* The maximum for major and minor version is chosen because it can
		then be represented as one combined integer. Since normal integers
		are capped at 2147483647, a little below the sqrt seems reasonable.
	* Don't change VERSION_MAX after going live, it'll change all versions!
"""


VERSION_MAX = 46340

PACKAGE_NAME_PATTERN = r'[a-z][a-z0-9_]{0,31}'
PACKAGE_NAME_MESSAGE = 'Package names may contain up to 32 lowercase letters, numbers and underscores ' + \
	'and must start with a letter.'

VERSION_REST_PATTERN = r'[^.][a-zA-Z0-9_\-.]+'
VERSION_PATTERN = '\d{1,5}(?:\.\d{1,5})?(?:\.' + VERSION_REST_PATTERN + ')?)?'
VERSION_MESSAGE = 'Version numbers should be formatted like 1.0.dev7, the first two being under {0:d}'.format(VERSION_MAX - 2)

VERSION_RANGE_PATTERN = '(?:[<>=\\z]=?(?:\*|\d{1,5})(?:\.(?:\*|\d{1,5})|\.|),?)+'
PACKAGE_RANGE_PATTERN = r'({0:s})({1:s})'.format(PACKAGE_NAME_PATTERN, VERSION_RANGE_PATTERN)

FILENAME_PATTERN = r'[a-zA-Z0-9_\-.]{1,32}'
FILENAME_MESSAGE = 'File and directory names may contain up to 32 alphanumeric characters, periods, ' + \
	'dashes and underscores.'


class VersionTooHigh(Exception):
	""" Version exceeded the maximum of VERSION_MAX """


class VersionRangeMismatch(Exception):
	""" Tried to add range selections that don't overlap. Also misused for duplicate packages. """


class VersionFormatError(Exception):
	""" Could not correctly interpret the package and/or version descrition string """


