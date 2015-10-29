
"""
	Parse packages and versions, which follow pip format.
"""

from argparse import ArgumentTypeError
from logging import warning
from re import fullmatch, findall, match  #todo: not in python 2.7


class VersionRangeMismatch(Exception):
	""" Tried to add range selections that don't overlap """


class VersionFormatError(Exception):
	""" Could not correctly interpret the package and/or version descrition string """


def intify(itrbl):
	return [int(val) if val else None for val in itrbl]


class VersionRange():
	"""
	Represent a range of versions. Versions have the format 'int.int' in this class.

	More deeply nested versions are explicitly assumed to be bugfixes that are otherwise
	compatible. Selection on those should therefore never be needed.

	Relies on Python tuple ordering: (1, 2) < (2, 1) and (1, 2) < (1, 3)
	"""
	def __init__(self, selections = '==*'):
		"""
		:param selections: A selection string, like '>=1.3,<2.0'.
		"""
		self.min = None
		self.min_inclusive = True
		self.max = None
		self.max_inclusive = True
		self.prefer_highest = True
		try:
			self.add_selections(selections, conflict='error')
		except VersionRangeMismatch:
			raise VersionRangeMismatch('"{0:s}" contains conflicting directives'.format(selections))

	@classmethod
	def raw(cls, min=None, max=None, min_inclusive=True, max_inclusive=True, prefer_highest=True, conflict='warning'):
		inst=cls('')
		assert type(min_inclusive) is bool and type(max_inclusive) is bool
		assert (min is None or type(min) is tuple) and (max is None or type(max) is tuple)
		assert (min is None or len(min) == 2) and (max is None or len(max) == 2)
		inst.update_values(min=min, max=max, min_inclusive=min_inclusive, max_inclusive=max_inclusive, conflict=conflict)
		inst.prefer_highest = prefer_highest
		return inst

	def update_values(self, min=None, max=None, min_inclusive=None, max_inclusive=None, conflict='warning'):
		"""
		Update the boundaries, handling possible conflicts.

		:param conflict: What to do in case of failure: 'silent', 'warning' or 'error'.
		"""
		def handle_conflict(msg):
			print('handling', conflict, 'for', msg)
			if conflict == 'silent':
				return
			elif conflict == 'warning':
				warning(msg)
			elif conflict == 'error':
				raise VersionRangeMismatch(msg)
			else:
				raise NotImplementedError('Unknown conflict mode "{0:}"'.format(conflict))
		if max_inclusive is not None and max is None:
			max = self.max
		if min_inclusive is not None and min is None:
			min = self.min
		#todo: problem: update from exclusive to inclusive (same value) shouldn't be possible as this expands the range
		if max is not None:
			""" New values have been provided. """
			if self.max is None or max < self.max or (max == self.max and not max_inclusive and self.max_inclusive):
				""" There is an old value, but ours is narrower, so we should update. """
				empty_range = False
				if self.min is not None:
					if max < self.min:
						empty_range = True
					elif max == self.min:
						if not (max_inclusive and (min_inclusive or self.min_inclusive)):
							empty_range = True
				if empty_range:
					""" The values of max and min create an empty range; update the lower one (which is the minimum). """
					print('max updated from', self.max, self.max_inclusive, 'to', max, max_inclusive, '(conflict mode)')  #todo
					handle_conflict('Maximum {0:s} conflicts with minimum {1:s}; minimum (highest value) takes precedence, but lower values not preferred.'
						.format('{0:d}.{1:d}'.format(*max), '{0:d}.{1:d}'.format(*self.min)))
					self.prefer_highest = False
				else:
					""" The value of max and min are not in conflict; simply update. """
					print('max updated from', self.max, self.max_inclusive, 'to', max, max_inclusive)  #todo
					self.max = max
					self.max_inclusive = max_inclusive
			else:
				""" The old value was narrower, so we ignore this new value. (This is no cause for a warning). """
				print('max NOT updated from', self.max, self.max_inclusive, 'to', max, max_inclusive)  #todo
		if min is not None:
			""" New values have been provided. """
			#todo: test this for max too
			if self.min is None or min > self.min or (min == self.min and not min_inclusive and self.min_inclusive):
				""" There is no old value, or there is an old value but ours is narrower, so we should update. """
				empty_range = False
				if self.max is not None:
					if min > self.max:
						empty_range = True
					elif min == self.max:
						print('  min == self.max', min, self.max)
						if not (min_inclusive and (max_inclusive or self.max_inclusive)):  #todo: doubtful line
							print('  min_inclusive or (max_inclusive or self.max_inclusive)', min_inclusive, max_inclusive, self.max_inclusive)
							empty_range = True
				if empty_range:
					""" The values of max and min create an empty range; update the lower one (which is the minimum). """
					print('min updated from', self.min, self.min_inclusive, 'to', min, min_inclusive, '(conflict mode)')  #todo
					print('min, self.max', min, self.max)
					handle_conflict('Minimum {0:s} conflicts with maximum {1:s}; minimum (highest value) takes precedence.'
						.format('{0:d}.{1:d}'.format(*min), '{0:d}.{1:d}'.format(*self.max)))
					self.max = min
					self.max_inclusive = True
					""" The value is fixed so preference has no effect, but set it just for future updates. """
					self.prefer_highest = False
				else:
					print('min updated from', self.min, self.min_inclusive, 'to', min, min_inclusive)  #todo
				""" Update to the target values independent of conflict """
				self.min = min
				self.min_inclusive = min_inclusive
			else:
				print('min NOT updated from', self.min, self.min_inclusive, 'to', min, min_inclusive)  #todo
		#todo: this still accepts >1.0,<1.1 which cannot match; leave it like that?

	def add_selections(self, selections, conflict = 'warning'):
		for version in selections.split(','):
			self.add_selection(version, conflict=conflict)

	def add_selection(self, selection, conflict = 'warning'):
		"""
		Restrict the range given a selection string

		:param selection: A single selection (without comma), like '>=1.3'.
		:param conflict: What to do in case of failure: 'silent', 'warning' or 'error'.
		"""
		print('BEFORE add_selection', selection, str(self))
		selection = selection.replace(' ', '').replace('=.', '=0.')
		if not selection:
			return
		if selection.count(','):
			raise Exception(('Version string "{0:s}" is incorrect. Perhaps you\'re trying to add a combined one; ' +
				'you should use add_selections for that').format(selection))
		if selection.count('.') > 1:
			raise VersionFormatError(('Version string "{0:s}" is incorrect. Perhaps it contains a version longer than 2 numbers ' +
				'(e.g. "3.14)" which is intentionally not supported. Version numbers beyond the second are for bugfixes only.').format(selection))
		regex = r'^[><=]=?(\d+|\*)(?:\.(\d*|\*))?$'
		if not match(regex, selection):
			raise VersionFormatError('Version string "{0:s}" not properly formatted according to "{1:s}".'.format(selection, regex))
		if selection.startswith('='):
			if '*' in selection:
				if match('^==?\*$', selection):
					return
				found = findall(r'^==?(\d+)\.\*$', selection)
				if not found:
					raise VersionFormatError('Version "{0:s}" not understood; * can appear as "==*" or "==nr.*" only.'.format(selection))
				major = int(found[0])
				self.update_values(min=(major, 0), max=(major + 1, 0), min_inclusive=True, max_inclusive=False, conflict=conflict)
			else:
				found = findall(r'^==?(\d+)(?:\.(\d*))?$', selection)
				if not found:
					raise VersionFormatError('Version "{0:s}" not understood; expecting "==nr" or "==nr.nr".'.format(selection))
				major, minor = intify(found[0])
				if minor is None:
					self.update_values(min=(major, 0), max=(major + 1, 0), min_inclusive=True, max_inclusive=False, conflict=conflict)
				else:
					print('yolo')
					self.update_values(min=(major, minor), max=(major, minor), min_inclusive=True, max_inclusive=True, conflict=conflict)
					print('yolo done')
		if selection.startswith('>'):
			incl = selection.startswith('>=')
			found = findall(r'^>=?(\d+)(?:\.(\d*))?$', selection)
			if not found:
				raise VersionFormatError('Version "{0:s}" not understood; expecting "nr" or "nr.nr" after the > or >=.'.format(selection))
			major, minor = intify(found[0])
			if minor is None:
				if incl:
					self.update_values(min=(major, 0), min_inclusive=True, conflict=conflict)
				else:
					self.update_values(min=(major + 1, 0), min_inclusive=True, conflict=conflict)
			else:
				self.update_values(min=(major, minor), min_inclusive=incl, conflict=conflict)
		if selection.startswith('<'):
			incl = selection.startswith('<=')
			found = findall(r'^<=?(\d+)(?:\.(\d*))?$', selection)
			if not found:
				raise VersionFormatError('Version "{0:s}" not understood; expecting "nr" or "nr.nr" after the < or <=.'.format(selection))
			major, minor = intify(found[0])
			""" Note that this is different from > because
				1)  <7 is <7.0 whereas >7 is >=8.0
				2)  <=7 is <8.0 whereas >7 is >=8.0 """
			if minor is None:
				if incl:
					self.update_values(max=(major + 1, 0), max_inclusive=False, conflict=conflict)
				else:
					self.update_values(max=(major, 0), max_inclusive=False, conflict=conflict)
			else:
				self.update_values(max=(major, minor), max_inclusive=incl, conflict=conflict)
		print('add_selection', selection, str(self))

	def choose(self, versions):
		"""
		Choose the highest version in the range.

		:param versions: Iterable of available versions.
		"""
		raise NotImplementedError('')
		#todo: prefer_highest
		#todo: try the first higher version
		#todo: if no higher versions, try the first lower one

	def _get_single(self):
		if self.min and self.max:
			if self.min == self.max:
				return self.min
			if self.min == (self.max[0], self.max[1] - 1):
				if self.min_inclusive:
					return self.min
				if self.max_inclusive:
					return self.max
			if self.min == (self.max[0], self.max[1] - 2):
				if not self.min_inclusive and not self.max_inclusive:
					return (self.max[0], self.max[1] - 1)

	def __eq__(self, other):
		if not type(self) is type(other):
			return False
		properties = ['min', 'max']
		if self.min is not None:
			properties.append('min_inclusive')
		if self.max is not None:
			properties.append('max_inclusive')
		if not self._get_single():
			properties.append('prefer_highest') #todo: tests
		for property in properties:
			if not getattr(self, property) == getattr(other, property):
				return False
		return True

	def intersection(self, other, conflict='warning'):
		if not type(self) is type(other):
			raise NotImplementedError('can only take intersection with other {0:s} objects, not {1:s}.'
				.format(str(type(self)), str(type(other))))
		self.update_values(min=other.min, max=other.max, min_inclusive=other.min_inclusive, max_inclusive=other.max_inclusive, conflict=conflict)
		self.prefer_highest = self.prefer_highest and other.prefer_highest

	def __and__(self, other):
		return self.intersection(other, conflict='silent')

	def tuple_to_str(self, tup):
		if tup[1] is None:
			return '{0:d}.*'.format(*tup)
		return '{0:d}.{1:d}'.format(*tup)

	def __str__(self):
		if self.min == self.max == None:
			return '==*'
		single = self._get_single()
		if single:
			return '=={0:d}.{1:d}'.format(*single)
		parts = []
		if self.min is not None:
			parts.append('>')
			if self.min_inclusive:
				parts.append('=')
			parts.append(self.tuple_to_str(self.min))
			if self.max is not None:
				parts.append(',')
		if self.max is not None:
			parts.append('<')
			if self.max_inclusive:
				parts.append('=')
			parts.append(self.tuple_to_str(self.max))
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


