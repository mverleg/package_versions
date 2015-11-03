
from package_versions import VersionRange, parse_dependency, parse_dependencies

print(VersionRange('==3'))
# >=3.0,<4.0
print(VersionRange('<=2.5,>1'))
# >=2.0,<=2.5
print(VersionRange('==2.*'))
# >=2.0,<3.0


print(VersionRange('<=2.5,>1') & VersionRange('==2.*'))
# >=2.0,<=2.5
print(VersionRange('<4.4') & VersionRange('>0,<=7'))
# >=1.0,<4.4
print(VersionRange('<4.4') & VersionRange('>5.3'))
# ==5.3 and an optional warning or error (due to the mismatch in range)


options = ['0.0.0', '2.8.', '2.1.unordered', '1.0.dev1', '2.2.words', '2.9.9', '999.999.0']
print(VersionRange('>=2.2,<2.9').choose(options))
# 2.8
print(VersionRange('>2.2,<2.8').choose(options))
# 2.8. and an optional warning or error (due to no match in range)
print(VersionRange('>2.2').choose(options))
# 999.999.0


print(parse_dependency('package>=3'))
# ('package', VersionRange(>=3.0))
print(parse_dependency('specialname123>2.0,<3'))
# ('specialname123', VersionRange(>=2.1,<3.0))
print(parse_dependencies('packA>1.3,<6\n#packskip==*\n\npackB<3.4#,>1.2'))
# OrderedDict([('packa', VersionRange(>=1.4,<6.0)), ('packb', VersionRange(<=3.3))])


