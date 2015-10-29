
from .versions_source import VersionRange


print(VersionRange('==3'))
# >=3.0,<4.0
print(VersionRange('<=2.5,>1'))
# >=2.0,<=2.5
print(VersionRange('==2.*'))
# >=2.0,<3.0


print(VersionRange('<=2.5,>1') & VersionRange('==2.*'))



