
from .settings import VERSION_MAX, VersionTooHigh


def str2nrrest(txt, mx=VERSION_MAX):
	if txt.count('.') == 0:
		major, minor, rest = '0' + txt, 0, ''
	elif txt.count('.') == 1:
		(major, minor), rest = txt.split('.'), ''
	else:
		parts = txt.split('.')
		major, minor = parts[:2]
		rest = '.'.join(parts[2:])
	major, minor = int(major), int(minor)
	if not (major < mx - 1 and minor < mx - 1):
		raise VersionTooHigh('version too high (major={0:d}, minor={1:d}, limit={2:d})'.format(major, minor, mx))
	return to_nr(major, minor, mx=mx), rest


def nrrest2str(nr, rest, mx=VERSION_MAX):
	(major, minor), rest = to_tup(nr, mx=mx), '.{0:s}'.format(rest) if rest else ''
	if not major < mx - 1:
		raise VersionTooHigh('version too high (input//limit={0:d}//{1:d}={2:d})'.format(nr, mx, major))
	return '{0:d}.{1:d}'.format(major, minor) + rest


def nr2str(nr, mx=VERSION_MAX):
	return nrrest2str(nr, '', mx=mx)


def str2nr(txt, mx=VERSION_MAX):
	return str2nrrest(txt, mx=mx)[0]


def to_tup(nr, mx=VERSION_MAX):
	return nr // mx, nr % mx


def to_nr(major, minor, mx=VERSION_MAX):
	return major * mx + minor


