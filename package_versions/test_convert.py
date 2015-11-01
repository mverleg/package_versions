
from pytest import raises
from .convert import str2nrrest, nrrest2str, str2nr, nr2str, VersionTooHigh, VERSION_MAX


def test_conversion():
	test_range = [0, 1, 2, 3, 5, 11, 17, 23, 87]
	test_rest = ['', '123', 'dev', '0..']
	test_max = [100, 241, VERSION_MAX]
	for major in test_range:
		for minor in test_range:
			for rest in test_rest:
				for mx in test_max:
					txt = '{0:d}.{1:d}.{2:s}'.format(major, minor, rest)
					nr, rest = str2nrrest(txt, mx=mx)
					back = nrrest2str(nr, rest, mx=mx)
					if not txt.rstrip('.') == back.rstrip('.'):
						raise AssertionError('converting back and forth (with rest part) did not yield ' +
							'the same result for "{0:s}" <-> "{1:s}"'.format(txt, back))
			txt = '{0:d}.{1:d}'.format(major, minor)
			nr = str2nr(txt, mx=mx)
			back = nr2str(nr, mx=mx)
			if not txt == back:
				raise AssertionError('converting back and forth (without rest part)' +
					'did not yield the same result for "{0:s}"'.format(txt))


def test_limit_errors():
	with raises(VersionTooHigh):
		str2nr('100.0', mx=100)
	with raises(VersionTooHigh):
		str2nr('0.100', mx=100)
	with raises(VersionTooHigh):
		str2nr('99.0', mx=100)
	with raises(VersionTooHigh):
		str2nr('0.99', mx=100)
	str2nr('98.0', mx=100)
	str2nr('0.98', mx=100)
	nr2str #todo


def test_max():
	pass


