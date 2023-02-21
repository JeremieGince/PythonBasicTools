from typing import Union, Optional, Tuple, Dict

from packaging.version import Version, parse, _cmpkey
import re
import enum


class MutableSegment(enum.Enum):
	__order__ = "MAJOR MINOR MICRO DEV PRE POST"
	MAJOR = "major"
	MINOR = "minor"
	MICRO = "micro"
	DEV = "dev"
	PRE = "pre"
	POST = "post"
	
	@classmethod
	def item_from_value(cls, value: str) -> "MutableSegment":
		for item in cls:
			if item.value == value:
				return item


class _Version:
	def __init__(
			self,
			epoch: Optional[int] = None,
			release: Optional[Tuple[int, ...]] = None,
			dev: Optional[Tuple[str, int]] = None,
			pre: Optional[Tuple[str, int]] = None,
			post: Optional[int] = None,
			local: Optional[str] = None,
	):
		self.epoch = epoch
		self.release = release
		self.dev = dev
		self.pre = pre
		self.post = post
		self.local = local


class MutableVersion(Version):
	DEFAULT_PRE_KEY = "rc"
	DEFAULT_DEV_KEY = "dev"
	
	def __init__(self, version: str):
		super().__init__(version)
		self._version = _Version(
			epoch=self._version.epoch,
			release=self._version.release,
			dev=self._version.dev,
			pre=self._version.pre,
			post=self._version.post,
			local=self._version.local,
		)
	
	@property
	def _key(self):
		return _cmpkey(
			self._version.epoch,
			self._version.release,
			self._version.pre,
			self._version.post,
			self._version.dev,
			self._version.local,
		)
	
	@_key.setter
	def _key(self, value):
		# workaround to allow a dynamic _key property
		pass
	
	@Version.release.setter
	def release(self, value):
		self._version.release = value
	
	@Version.epoch.setter
	def epoch(self, value):
		self._version.epoch = value
	
	@Version.dev.setter
	def dev(self, value):
		if isinstance(value, str):
			value = (value, self.dev)
		elif isinstance(value, int):
			value = (self._version.dev[0] if self._version.dev else self.DEFAULT_DEV_KEY, value)
		self._version.dev = value
	
	@Version.pre.setter
	def pre(self, value):
		if isinstance(value, str):
			value = (value, self.pre[1])
		elif isinstance(value, int):
			value = (self._version.pre[0] if self._version.pre else self.DEFAULT_PRE_KEY, value)
		self._version.pre = value
	
	@Version.post.setter
	def post(self, value):
		self._version.post = value
	
	@Version.local.setter
	def local(self, value):
		self._version.local = value
	
	@Version.major.setter
	def major(self, value):
		self._version.release = (value, *self._version.release[1:])
	
	@Version.minor.setter
	def minor(self, value):
		self._version.release = (self._version.release[0], value, *self._version.release[2:])
	
	@Version.micro.setter
	def micro(self, value):
		self._version.release = (self._version.release[0], self._version.release[1], value)


def get_version_from_file(
		file_path: str = "./__init__.py",
		attr: str = "__version__",
		re_as_str: bool = False,
) -> Union[str, Version]:
	"""
	Get the version of a package from a file.

	:param file_path: The path to the file.
	:type file_path: str
	:param attr: The name of the attribute containing the version. If attr is None or empty, the version will be read
		from the first line of the file.
	:type attr: str
	:param re_as_str: If True, the version will be returned as a string.
	:type re_as_str: bool
	
	:return: The version of the package.
	"""
	version_raw_str = ""
	regex_expr = rf"{attr}\s*=\s*['\"](?P<version>.+)['\"]"
	with open(file_path, "r") as f:
		if attr is None or attr == "":
			version_raw_str = f.readline()
		else:
			re_search = re.search(regex_expr, f.read())
			if re_search is not None:
				version_raw_str = re_search.group("version")
	
	version = parse(version_raw_str)
	if re_as_str:
		version = str(version)
	return version


def set_version_in_file(
		version: Union[str, Version],
		file_path: str = "./__init__.py",
		attr: str = "__version__",
) -> str:
	"""
	Set the version of a package in a file.

	:param version: The version to set.
	:type version: Union[str, Version]
	:param file_path: The path to the file.
	:type file_path: str
	:param attr: The name of the attribute containing the version. If attr is None or empty, the version will be read
		from the first line of the file. Note that if attr is None or empty the output file will be overwrite and will
		only contain the version.
	:type attr: str
	
	:return: The version of the package.
	:rtype: str
	"""
	version_str = str(version)
	regex_expr = rf"{attr}\s*=\s*['\"].+['\"]"
	with open(file_path, "r") as f:
		file_content = f.read()
		if attr is None or attr == "":
			file_content = f"{version_str}"
		else:
			file_content = re.sub(regex_expr, f"{attr} = '{version_str}'", file_content)
	with open(file_path, "w") as f:
		f.write(file_content)
	return version_str


def increment_version(
		version: Union[str, Version],
		re_as_str: bool = False,
		**kwargs,
) -> Union[str, Version]:
	"""
	Increment the version of a package. The version can be a string or a Version object.
	To increment a segment, use the name of the segment as a keyword argument and set its value to the amount to
	increment.
	
	:param version: The version to update.
	:type version: Union[str, Version]
	:param re_as_str: If True, the version will be returned as a string.
	:type re_as_str: bool
	:param kwargs: The segments to update.
	
	:keyword int major: The amount to increment the major segment.
	:keyword int minor: The amount to increment the minor segment.
	:keyword int micro: The amount to increment the micro segment.
	:keyword int pre: The amount to increment the pre segment.
	:keyword int post: The amount to increment the post segment.
	:keyword int dev: The amount to increment the dev segment.
	
	:return: The updated version.
	:rtype: MutableVersion
	"""
	segments_names = [seg.value for seg in MutableSegment]
	segments_to_types = {
		"major": int,
		"minor": int,
		"micro": int,
		"pre"  : int,
		"post" : int,
		"dev"  : int,
	}
	if isinstance(version, str):
		version = MutableVersion(version)
	else:
		version = MutableVersion(str(version))
	for key in kwargs:
		if key not in segments_names:
			raise ValueError(f"Invalid segment name: '{key}'.")
		if not isinstance(kwargs[key], int):
			raise TypeError(f"Invalid type for segment {key}: {type(kwargs[key])}")
		old_value = getattr(version, key, 0)
		if old_value is None:
			old_value = 0
		if isinstance(old_value, tuple):
			old_value = old_value[1]
		setattr(version, key, old_value + int(kwargs[key]))
	if re_as_str:
		version = str(version)
	return version


def infer_affected_version_segment_from_msg(
		msg: str,
		segments_to_regex: Dict[MutableSegment, str] = None,
) -> str:
	"""
	Infer the affected version segment from a commit message. The commit message is matched against a dictionary of
	regular expressions. The key of the dictionary is the segment name and the value is the regular expression to
	match.
	
	:param msg: The commit message.
	:type msg: str
	:param segments_to_regex: The dictionary of regular expressions.
	:type segments_to_regex: Dict[MutableSegment, str]
	
	:return: The affected version segment.
	:rtype: str
	"""
	segments = [seg for seg in MutableSegment]
	if segments_to_regex is None:
		segments_to_regex = {}
	default_segments_to_regex = {
		MutableSegment.MAJOR: r"major|breaking|break|bump major|bump major version|bump major version number",
		MutableSegment.MINOR: r"minor|feature|feat|bump minor|bump minor version|bump minor version number",
		MutableSegment.MICRO: r"micro|patch|fix|test|docs|style|refactor|perf|bump micro|bump micro version|"
		r"bump micro version number|doc|documentation|style|styling|refactoring|performance|performance improvement|"
		r"testing|tests|tests improvement|tests improvements|tests improvements",
		MutableSegment.PRE  : r"pre|prerelease|bump pre|bump pre version|bump pre version number",
		MutableSegment.POST : r"post|bump post|bump post version|bump post version number",
		MutableSegment.DEV  : r"dev|bump dev|bump dev version|bump dev version number",
	}
	for segment in segments:
		if re.search(segments_to_regex.get(segment, default_segments_to_regex[segment]), msg, re.IGNORECASE):
			return segment.value
	return MutableSegment.PRE.value




