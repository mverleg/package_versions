
from package_versions import VersionRange


print(VersionRange('==3'))
# >=3.0,<4.0
print(VersionRange('<=2.5,>1'))
# >=2.0,<=2.5
print(VersionRange('==2.*'))
# >=2.0,<3.0


print(VersionRange('<=2.5,>1') & VersionRange('==2.*'))
#>=2.0,<=2.5
print(VersionRange('<4.4') & VersionRange('>0,<=7'))
#>=1.0,<4.4
print(VersionRange('<4.4') & VersionRange('>5.3'))
#==5.3 and an optional warning or error (due to the mismatch in range)

