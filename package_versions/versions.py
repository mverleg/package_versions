
"""
	Parse packages and versions, which follow pip format.
"""

from logging import warning
from re import findall, match
from convert import to_tup, to_nr
from .settings import VersionRangeMismatch, VersionFormatError, VERSION_MAX

pymin, pymax = min, max


def intify(itrbl):
	return [int(val) if val else None for val in itrbl]


class VersionRange():
	"""
	Represent a range of versions. Versions have the format 'int.int' in this class.

	More deeply nested versions are explicitly assumed to be bugfixes that are otherwise
	compatible. Selection on those should therefore never be needed.
	"""
	def __init__(self, selections='==*', mx=VERSION_MAX):
		"""
		:param selections: A selection string, like '>=1.3,<2.0'.
		"""
		self.limit = mx
		self.min = 0
		self.max = self.highest
		self.prefer_highest = True
		try:
			self.add_selections(selections, conflict='error')
		except VersionRangeMismatch:
			raise VersionRangeMismatch('"{0:s}" contains conflicting directives'.format(selections))

	@property
	def highest(self):
		return (self.limit + 1) * self.limit

	@classmethod
	def raw(cls, min=(0, 0), max=None, min_inclusive=True, max_inclusive=True, prefer_highest=True, conflict='warning', mx=VERSION_MAX):
		inst=cls(mx=mx)
		assert type(min_inclusive) is bool and type(max_inclusive) is bool
		assert (min is None or type(min) is tuple) and (max is None or type(max) is tuple)
		assert (min is None or len(min) == 2) and (max is None or len(max) == 2)
		min = -1 if min is None else inst.to_nr(*min)
		max = inst.highest + 1 if max is None else inst.to_nr(*max)
		if not min_inclusive:
			min += 1
		if not max_inclusive:
			max -= 1
		inst.update_values(min=min, max=max, conflict=conflict)
		inst.prefer_highest = prefer_highest
		return inst

	def to_tup(self, nr):
		return to_tup(nr, mx=self.limit)

	def to_nr(self, major, minor):
		return to_nr(major, minor, mx=self.limit)

	def update_values(self, min=None, max=None, conflict='warning'):
		"""
		Update the boundaries, handling possible conflicts.

		:param conflict: What to do in case of failure: 'silent', 'warning' or 'error'.
		"""
		conflict_txt = None
		if min is not None:
			if min > self.min:
				if min > self.max:
					self.max = self.highest
					self.prefer_highest = False
					conflict_txt = 'Minimum {0:s} conflicts with maximum {1:s}; minimum is higher so it takes precedence, but lower values in range are not preferred.'.format('{0:d}.{1:d}'.format(*self.to_tup(min)), '{0:d}.{1:d}'.format(*self.to_tup(self.max)))
				self.min = min
		if max is not None:
			if max < self.max:
				if max >= self.min:
					self.max = max
				else:
					self.prefer_highest = False
					conflict_txt = 'Maximum {0:s} conflicts with minimum {1:s}; minimum is higher so takes it precedence, but lower values in range are now preferred.'.format('{0:d}.{1:d}'.format(*self.to_tup(max)), '{0:d}.{1:d}'.format(*self.to_tup(self.min)))
		if conflict_txt:
			if conflict == 'silent':
				return
			elif conflict == 'warning':
				warning(conflict_txt)
			elif conflict == 'error':
				raise VersionRangeMismatch(conflict_txt)
			else:
				raise NotImplementedError('Unknown conflict mode "{0:}"'.format(conflict))

	def add_selections(self, selections, conflict = 'warning'):
		if '_' in selections:
			self.prefer_highest = False
			selections = selections.replace('_', '')
		for version in selections.split(','):
			self.add_selection(version, conflict=conflict)

	def add_selection(self, selection, conflict = 'warning'):
		"""
		Restrict the range given a selection string

		:param selection: A single selection (without comma), like '>=1.3'.
		:param conflict: What to do in case of failure: 'silent', 'warning' or 'error'.
		"""
		selection = selection.replace(' ', '').replace('=.', '=0.')
		if not selection:
			return
		if selection.count(',') or selection.count('_'):
			raise Exception(('Version string "{0:s}" is incorrect. Perhaps you\'re trying to add a combined one; ' +
				'you should use add_selections for that').format(selection))
		if selection.count('.') > 1:
			raise VersionFormatError(('Version string "{0:s}" is incorrect. Perhaps it contains a version longer than 2 numbers ' +
				'(e.g. "3.14)" which is intentionally not supported. Version numbers beyond the second are for bugfixes only.').format(selection))
		regex = r'^([><=]=?)(\d+|\*)(?:\.(\d*|\*))?$'
		found = findall(regex, selection)
		if not found:
			raise VersionFormatError('Version string "{0:s}" not properly formatted according to "{1:s}".'.format(selection, regex))
		operation, majorstr, minorstr = found[0]
		if majorstr == '*':
			return
		major = int(majorstr)
		if minorstr == '*':
			self.update_values(conflict=conflict,
				min = self.to_nr(major, 0),
				max = self.to_nr(major + 1, 0) - 1,
			)
			return
		exclusive = int(not operation.endswith('='))
		major_only = int(not minorstr)
		nr = self.to_nr(major, int(minorstr or 0))
		if operation.startswith('='):
			self.update_values(conflict=conflict,
				min = nr,
				max = nr + major_only * self.limit - major_only,
			)
		elif operation.startswith('<'):
			self.update_values(conflict=conflict,
				max = nr - exclusive + (not exclusive) * (major_only * self.limit - major_only),
			)
		elif operation.startswith('>'):
			self.update_values(conflict=conflict,
				min = nr + exclusive + exclusive * (major_only * self.limit - major_only),
			)
		else:
			raise VersionFormatError('Version (in)equality operator "{0:s}" not recognized. ' +
				'Full operation "{1:s}"'.format(operation, selection))

	def choose(self, versions):
		"""
		Choose the highest version in the range.

		:param versions: Iterable of available versions.
		"""
		raise NotImplementedError('')
		#todo: prefer_highest
		#todo: try the first higher version
		#todo: if no higher versions, try the first lower one

	def __eq__(self, other):
		if not type(self) is type(other):
			return False
		if not self.min == other.min:
			return False
		if not self.max == other.max:
			return False
		if self.min > 0:
			if not self.prefer_highest == other.prefer_highest:
				return False
		return True

	def intersection(self, other, conflict='warning'):
		if not type(self) is type(other):
			raise NotImplementedError('can only take intersection with other {0:s} objects, not {1:s}.'
				.format(str(type(self)), str(type(other))))
		intersection = VersionRange.raw(min=self.min, max=self.max, conflict=conflict)
		intersection.update_values(min=other.min, max=other.max, conflict=conflict)
		intersection.prefer_highest = self.prefer_highest and other.prefer_highest
		return intersection

	def __and__(self, other):
		return self.intersection(other, conflict='silent')

	def __str__(self):
		if self.min <= 0 and self.max >= self.highest:
			return '==*'
		min1, min2 = self.to_tup(self.min)
		if self.min == self.max:
			return '=={0:d}.{1:d}'.format(min1, min2)
		max1, max2 = self.to_tup(self.max)
		parts = []
		if self.min > 0:
			parts.append(
				'>={0:d}.{1:d}'.format(min1, min2)
			)
			if self.max < self.highest:
				parts.append(',')
		if self.max < self.highest:
			if max2 == self.limit - 1:
				if min2 == 0 and min1 == max1 - 2:
					return '=={0:d}.*'.format(min1)
				else:
					parts.append(
						'<{0:d}.0'.format(max1 + 1)
					)
			else:
				parts.append(
					'<={0:d}.{1:d}'.format(max1, max2)
				)
		if not self.prefer_highest and self.min > 0:
			parts.append('_')
		return ''.join(parts)


def parse_dependency(txt):
	txt = txt.split('#')[0]
	try:
		package = findall(r'^([a-zA-Z0-9_\-]*)[><=*\\z]', txt)[0]
		versions = findall(r'^[a-zA-Z0-9_\-]*([><=*][><=*0-9. ]*)$', txt)[0]
	except IndexError:
		raise VersionFormatError('Given text "{0:s}" does not seem to be formatted correctly'.format(txt))
	vrange = VersionRange(versions)
	return package, vrange


