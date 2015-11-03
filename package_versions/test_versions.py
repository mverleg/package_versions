
from collections import OrderedDict
from pytest import raises
from .versions import VersionRange, parse_dependency, parse_dependencies
from .settings import VersionRangeMismatch, VersionFormatError


def test_range_equality():
	range1 = VersionRange.raw(min=(1, 3), max=(2, 0), min_inclusive=True, max_inclusive=False)
	range2 = VersionRange.raw(min=(1, 3), max=(2, 0), min_inclusive=True, max_inclusive=False)
	assert range1 == range2
	range3 = VersionRange.raw(min=(1, 3), max=(2, 0), min_inclusive=False, max_inclusive=False)
	range4 = VersionRange.raw(min=(1, 3), max=(2, 1), min_inclusive=True, max_inclusive=False)
	range11 = VersionRange.raw(min=(3, 1), max=(2, 0), min_inclusive=True, max_inclusive=False)
	assert not range1 == range3
	assert not range1 == range4
	assert not range1 == range11
	range5 = VersionRange.raw(min=None, min_inclusive=True)
	range6 = VersionRange.raw(min=None, min_inclusive=False)
	range7 = VersionRange.raw(max=None, max_inclusive=True)
	range8 = VersionRange.raw(max=None, max_inclusive=False)
	assert range5 == range6
	assert range7 == range8
	range9 = VersionRange.raw(min=None, max=None)
	range10 = VersionRange.raw(min=None, max=None)
	assert range9 == range10


def test_range_raw_checks():
	with raises(AssertionError):
		VersionRange.raw(min=(1, 3, 5))
	with raises(AssertionError):
		VersionRange.raw(max=(1, 3, 5))
	with raises(AssertionError):
		VersionRange.raw(min='1.3')
	with raises(AssertionError):
		VersionRange.raw(min='1.3')
	with raises(AssertionError):
		VersionRange.raw(min_inclusive=12)
	with raises(AssertionError):
		VersionRange.raw(max_inclusive=12)


def test_range_checks():
	with raises(VersionRangeMismatch):
		VersionRange('<=2.2').add_selection('>2.3', conflict='error')
	with raises(VersionRangeMismatch):
		VersionRange('>2.3,<=2.2')
	with raises(VersionRangeMismatch):
		VersionRange('<=2.2,>2.3')
	with raises(VersionRangeMismatch):
		VersionRange('==2.*,<=1.9')
	with raises(VersionRangeMismatch):
		VersionRange('>2,<3,<1')


def test_range_noconflict():
	vr = VersionRange('>4.2,<5')
	vr.add_selection('==4.3', conflict='silent')
	assert vr == VersionRange.raw(min=(4, 3), max=(4, 3), min_inclusive=True, max_inclusive=True)
	vr = VersionRange('>4.2,<5')
	vr.add_selection('==4.*', conflict='silent')
	assert vr == VersionRange.raw(min=(4, 2), max=(5, 0), min_inclusive=False, max_inclusive=False)
	vr = VersionRange('>4.0,<5')
	vr.add_selection('<4.5', conflict='silent')
	assert vr == VersionRange.raw(min=(4, 0), max=(4, 5), min_inclusive=False, max_inclusive=False)
	vr = VersionRange('>4.0,<5')
	vr.add_selection('>=4.5', conflict='silent')
	assert vr == VersionRange.raw(min=(4, 5), max=(5 ,0), min_inclusive=True, max_inclusive=False)
	vr = VersionRange('>4.0,<5')
	vr.add_selections('>4.2,<4.8', conflict='silent')
	assert vr == VersionRange.raw(min=(4, 2), max=(4, 8), min_inclusive=False, max_inclusive=False)
	vr = VersionRange('>4.0,<5')
	vr.add_selections('>=4.2,<=4.8', conflict='silent')
	assert vr == VersionRange.raw(min=(4, 2), max=(4, 8), min_inclusive=True, max_inclusive=True)
	vr = VersionRange('>4.0,<5')
	vr.add_selections('>4.5,<5.5', conflict='silent')
	assert vr == VersionRange.raw(min=(4, 5), max=(5, 0), min_inclusive=False, max_inclusive=False)
	vr = VersionRange('>4.0,<5')
	vr.add_selections('>=2.5,<=4.8', conflict='silent')
	assert vr == VersionRange.raw(min=(4, 0), max=(4, 8), min_inclusive=False, max_inclusive=True)
	vr = VersionRange('>4.0,<5')
	vr.add_selections('>3.15,<=5.0', conflict='silent')
	assert vr == VersionRange.raw(min=(4, 0), max=(5, 0), min_inclusive=False, max_inclusive=False)


def test_range_conflict_resolution():
	vr = VersionRange('>2.3')
	vr.add_selection('<=2.2', conflict='silent')
	assert vr == VersionRange.raw(min=(2, 3), max=None, min_inclusive=False, prefer_highest=False)
	vr = VersionRange('<=2.2')
	vr.add_selection('>2.3', conflict='silent')
	assert vr == VersionRange.raw(min=(2, 3), max=None, min_inclusive=False, prefer_highest=False)
	vr = VersionRange('>=2.3')
	vr.add_selection('<2.2', conflict='silent')
	assert vr == VersionRange.raw(min=(2, 3), max=None, min_inclusive=True, prefer_highest=False)
	vr = VersionRange('<2.2')
	vr.add_selection('>=2.3', conflict='silent')
	assert vr == VersionRange.raw(min=(2, 3), max=None, min_inclusive=True, prefer_highest=False)
	vr = VersionRange('>4.0,<5')
	vr.add_selection('<3.0', conflict='silent')
	assert vr == VersionRange.raw(min=(4, 0), max=(5, 0), min_inclusive=False, max_inclusive=False, prefer_highest=False)
	vr = VersionRange('>4.0,<5')
	vr.add_selection('>=5.0', conflict='silent')
	assert vr == VersionRange.raw(min=(5, 0), max=None, min_inclusive=True, prefer_highest=False)
	vr = VersionRange('>=4.0,<=5')
	vr.add_selection('<=3.0', conflict='silent')
	assert vr == VersionRange.raw(min=(4, 0), max=(6, 0), min_inclusive=True, max_inclusive=False, prefer_highest=False)
	vr = VersionRange('>=4.0,<=5')
	vr.add_selection('>5.0', conflict='silent')
	assert vr == VersionRange.raw(min=(5, 0), max=(6, 0), min_inclusive=False, max_inclusive=False)
	vr = VersionRange('>4.0,<5')
	vr.add_selection('>=7.0', conflict='silent')
	assert vr == VersionRange.raw(min=(7, 0), max=None, min_inclusive=True, prefer_highest=False)
	vr = VersionRange('>4.0,<5')
	vr.add_selection('>7.0', conflict='silent')
	assert vr == VersionRange.raw(min=(7, 0), max=None, min_inclusive=False, prefer_highest=False)
	vr = VersionRange('<140')
	vr.add_selection('<=140', conflict='silent')
	assert vr == VersionRange.raw(max=(140, 0), max_inclusive=False)
	vr = VersionRange('>=999.99')
	vr.add_selection('>999.99', conflict='silent')
	assert vr == VersionRange.raw(min=(999, 99), min_inclusive=False)


def test_conflict_errors():
	vr = VersionRange('>4.0,<5')
	with raises(VersionRangeMismatch):
		vr.add_selection('>7.0', conflict='error')
	vr = VersionRange('>4.0,<5')
	with raises(VersionRangeMismatch):
		vr.add_selection('<3.0', conflict='error')


def test_make_range():
	""" Note: single equality like =1.7 isn't officially supported, but don't break it without reason. """
	assert VersionRange('==*') == VersionRange('=*') == VersionRange.raw(min=None, max=None)
	assert VersionRange('==1.*') == VersionRange('=1.*') == VersionRange.raw(min=(1, 0), max=(2, 0), min_inclusive=True, max_inclusive=False)
	assert VersionRange('==2.7') == VersionRange('=2.7') == VersionRange.raw(min=(2, 7), max=(2, 7), min_inclusive=True, max_inclusive=True)
	assert VersionRange('>1.0') == VersionRange.raw(min=(1, 0), min_inclusive=False)
	assert VersionRange('==1.') == VersionRange('==1') == VersionRange.raw(min=(1, 0), min_inclusive=True, max=(2, 0), max_inclusive=False)
	assert VersionRange('>1.') == VersionRange('>1') == VersionRange.raw(min=(2, 0), min_inclusive=True)
	assert VersionRange('>=1.') == VersionRange('>=1') == VersionRange.raw(min=(1, 0), min_inclusive=True)
	assert VersionRange('<1.') == VersionRange('<1') == VersionRange.raw(max=(1, 0), max_inclusive=False)
	assert VersionRange('<=1.') == VersionRange('<=1') == VersionRange.raw(max=(2, 0), max_inclusive=False)
	assert VersionRange('>=3.4') == VersionRange.raw(min=(3, 4), min_inclusive=True)
	assert VersionRange('<9.0') == VersionRange.raw(max=(9, 0), max_inclusive=False)
	assert VersionRange('<=3.4') == VersionRange.raw(max=(3, 4), max_inclusive=True)
	assert VersionRange('>=3.5_') == VersionRange.raw(min=(3, 5), min_inclusive=True, prefer_highest=False)
	assert VersionRange('>3.5_') == VersionRange.raw(min=(3, 5), min_inclusive=False, prefer_highest=False)
	assert VersionRange.raw(min=(2, 2), max=(2, 3), min_inclusive=True, max_inclusive=False) == VersionRange('>=2.2,<2.3')
	assert VersionRange.raw(min=(1, 3), max=(2, 0), min_inclusive=True, max_inclusive=False) == VersionRange('>=1.3,<2.0')


def test_equivalent_expressions():
	assert VersionRange('==0.0') == VersionRange('==.0')
	assert VersionRange('==0.') == VersionRange('==.')
	assert VersionRange('<=3.5') == VersionRange('<=3.5_')
	assert VersionRange('<3.5') == VersionRange('<3.5_')


def test_incorrect_version():
	with raises(VersionFormatError):
		VersionRange('hello world')
	with raises(VersionFormatError):
		VersionRange('>=1.0.0')
	with raises(VersionFormatError):
		VersionRange('<1.0.0')
	with raises(VersionFormatError):
		VersionRange('=1.0.0')
	with raises(VersionFormatError):
		VersionRange('package==1.0')
	with raises(VersionFormatError):
		VersionRange('<=')
	with raises(VersionFormatError):
		VersionRange('9=')


def test_intersection():
	assert VersionRange('==1.0') & VersionRange('==1.0') == VersionRange('==1.0')
	assert VersionRange('>2.0') & VersionRange('<5') == VersionRange('>2.0,<5')
	assert VersionRange('>2,<=6') & VersionRange('>4,<8') == VersionRange('>4,<=6')
	assert VersionRange('>=2,<4') & VersionRange('>5.0,<=7.0') == VersionRange('>5.0,<=7.0_')
	assert VersionRange('>5.0,<=7.0') & VersionRange('>=2,<4') == VersionRange('>5.0,<=7.0_')


def test_range_repr():
	for repr in ('>=1.3,<2.0', '==1.7', '==*', '>=2.3_'):
		assert str(VersionRange(repr)) == repr
	assert str(VersionRange('=37.0')) == '==37.0'
	assert str(VersionRange('==2.*,<2.5')) in ('>=2.0,<2.5', '>=2.0,<=2.4')
	assert str(VersionRange('<=1.4,>=1.4')) == '==1.4'
	assert str(VersionRange('==1.*')) == '>=1.0,<2.0'
	assert str(VersionRange('>=2.2,<2.3')) == '==2.2'
	assert str(VersionRange('>2.2,<=2.3')) == '==2.3'
	assert str(VersionRange('>2.2,<2.4')) == '==2.3'
	assert str(VersionRange('<3.0,>1.0')) in ('>1.0,<3.0', '>=1.1,<3.0')
	assert str(VersionRange('<3.0,>1.0_')) in ('>1.0,<3.0_', '>=1.1,<3.0_')


def test_parse_dependency():
	assert parse_dependency('package==*') == ('package', VersionRange('==*'))
	assert parse_dependency('package==2.7') == ('package', VersionRange('==2.7'))
	assert parse_dependency('package>=3') == ('package', VersionRange('>=3'))
	assert parse_dependency('specialname123>2.0,<3') == ('specialname123', VersionRange('>2.0,<3'))


def test_parse_dependencies():
	inp = """PACK1>1.7\npack2>1.3,<6\ndup<=2.7\n#pack3==*\n\npack4<3.4#,>1.2\ndup>2.0#\n#"""
	ref = OrderedDict([
		('pack1', VersionRange('>1.7')),
		('pack2', VersionRange('>1.3,<6')),
		('dup', VersionRange('>2.0,<=2.7')),
		('pack4', VersionRange('<3.4')),
	])
	assert parse_dependencies(inp) == ref
	with raises(VersionRangeMismatch):
		assert parse_dependencies('dup<=2.7\ndup>2.0', duplicates='error') == ref


def test_comments():
	package1, range1 = parse_dependency('package>=1.0#,<2.0')
	assert range1 == VersionRange('>=1.0')
	package2, range2=parse_dependency('package>=1. # hello world')
	assert package2 == 'package'
	assert range2 == VersionRange('>=1')
	assert parse_dependency('#package>=1.0') is None


def test_choose():
	options = ['0.0.0', '2.8.', '2.1.unordered', '1.0.dev1', '2.2.words', '2.9.9', '999.999.0']
	assert VersionRange('>=2.2,<2.9').choose(options) == '2.8.'
	assert VersionRange('>=2.2,<=2.9').choose(options) == '2.9.9'
	assert VersionRange('>2.2,<2.9').choose(options) == '2.8.'
	assert VersionRange('>2.2,<=2.9').choose(options) == '2.9.9'
	assert VersionRange('>2.2,<2.8').choose(options) == '2.8.'
	assert VersionRange('>2.2,<2.7').choose(options) == '2.8.'
	assert VersionRange('>2.2').choose(options) == '999.999.0'
	assert VersionRange('>=2.2').choose(options) == '999.999.0'
	assert VersionRange('<2.9').choose(options) == '2.8.'
	assert VersionRange('<=2.9').choose(options) == '2.9.9'
	assert VersionRange('>2.9,<7.0').choose(options[:-1]) == '2.9.9'
	assert VersionRange('>10,<20').choose(options[:-1]) == '2.9.9'


#todo: test and make choosing based on 3rd part of version (alphabetic?)


