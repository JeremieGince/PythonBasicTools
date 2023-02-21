import functools
import unittest
from typing import Optional

from packaging.version import InvalidVersion

from pythonbasictools.packaging_tools import (
	MutableSegment,
	get_version_from_file,
	set_version_in_file,
	increment_version,
	infer_affected_version_segment_from_msg,
)
import os


def clone_file_decorator(_func=None, *, file_path: str, clone_path: Optional[str] = None, rm_clone: bool = True):
	if clone_path is None:
		basename, ext = os.path.splitext(file_path)
		clone_path = f"{basename}_clone{ext}"
	
	def decorator_func(func):
		@functools.wraps(func)
		def wrapper(*args, **kwargs):
			with open(file_path, "r") as f:
				file_content = f.read()
			with open(clone_path, "w") as f:
				f.write(file_content)
			out = func(*args, **kwargs)
			if rm_clone:
				os.remove(clone_path)
			return out
	
		return wrapper
	
	if _func is None:
		return decorator_func
	else:
		return decorator_func(_func)


class TestVersioning(unittest.TestCase):
	def test_get_version(self):
		file_path = "version_mock_files/_init.py"
		if not os.path.exists(file_path):
			file_path = f"tests/packaging_tools/{file_path}"
		
		self.assertEqual(
			get_version_from_file(
				file_path=file_path,
				attr="__version__",
				re_as_str=True,
			),
			"0.0.1"
		)
		self.assertEqual(
			get_version_from_file(
				file_path=file_path,
				attr="__version_sq__",
				re_as_str=True,
			),
			"0.0.1"
		)
		self.assertEqual(
			get_version_from_file(
				file_path=file_path,
				attr="__version_beta__",
				re_as_str=True,
			),
			"0.0.1b3"
		)
		self.assertEqual(
			get_version_from_file(
				file_path=file_path,
				attr="__version_b__",
				re_as_str=True,
			),
			"0.0.1b3"
		)
		with self.assertRaises(InvalidVersion) as cm:
			get_version_from_file(
				file_path=file_path,
				attr="__version_bad__",
				re_as_str=True,
			)
	
	@clone_file_decorator(file_path="version_mock_files/_init.py", clone_path="version_mock_files/_init_clone.py")
	def test_set_version(self):
		self.assertEqual(
			set_version_in_file(
				version='0.0.2',
				file_path="version_mock_files/_init_clone.py",
				attr="__version_sq__",
			),
			get_version_from_file(
				file_path="version_mock_files/_init_clone.py",
				attr="__version_sq__",
				re_as_str=True,
			)
		)
		self.assertEqual(
			set_version_in_file(
				version="0.0.3",
				file_path="version_mock_files/_init_clone.py",
				attr="__version__",
			),
			get_version_from_file(
				file_path="version_mock_files/_init_clone.py",
				attr="__version__",
				re_as_str=True,
			)
		)
	
	def test_increment_version(self):
		self.assertEqual(
			increment_version("0.0.1", micro=1, re_as_str=True),
			"0.0.2"
		)
		# test for every segments
		self.assertEqual(
			increment_version("0.0.1", major=1, re_as_str=True),
			"1.0.1"
		)
		self.assertEqual(
			increment_version("0.0.1", minor=1, re_as_str=True),
			"0.1.1"
		)
		self.assertEqual(
			increment_version("0.0.1.dev1", dev=1, re_as_str=True),
			"0.0.1.dev2"
		)
		self.assertEqual(
			increment_version("0.0.1", dev=1, re_as_str=True),
			"0.0.1.dev1"
		)
		self.assertEqual(
			increment_version("0.0.1-beta1", pre=1, re_as_str=True),
			"0.0.1b2"
		)
		self.assertEqual(
			increment_version("0.0.1", pre=1, re_as_str=True),
			"0.0.1rc1"
		)
		self.assertEqual(
			increment_version("0.0.1rc1", pre=1, re_as_str=True),
			"0.0.1rc2"
		)
		self.assertEqual(
			increment_version("0.0.1a1", pre=1, re_as_str=True),
			"0.0.1a2"
		)
	
	def test_infer_affected_version_segment_from_msg_in_names(self):
		self.assertEqual(
			infer_affected_version_segment_from_msg("major"),
			MutableSegment.MAJOR.value
		)
		self.assertEqual(
			infer_affected_version_segment_from_msg("minor"),
			MutableSegment.MINOR.value
		)
		self.assertEqual(
			infer_affected_version_segment_from_msg("micro"),
			MutableSegment.MICRO.value
		)
		self.assertEqual(
			infer_affected_version_segment_from_msg("dev"),
			MutableSegment.DEV.value
		)
		self.assertEqual(
			infer_affected_version_segment_from_msg("pre"),
			MutableSegment.PRE.value
		)
		self.assertEqual(
			infer_affected_version_segment_from_msg("post"),
			MutableSegment.POST.value
		)
	
	def test_infer_affected_version_segment_from_msg_in_complicated(self):
		self.assertEqual(
			infer_affected_version_segment_from_msg("patch"),
			MutableSegment.MICRO.value
		)
		self.assertEqual(
			infer_affected_version_segment_from_msg("prerelease"),
			MutableSegment.PRE.value
		)
		self.assertEqual(
			infer_affected_version_segment_from_msg("feature"),
			MutableSegment.MINOR.value
		)
		self.assertEqual(
			infer_affected_version_segment_from_msg("tests"),
			MutableSegment.MICRO.value
		)
		self.assertEqual(
			infer_affected_version_segment_from_msg("perf"),
			MutableSegment.MICRO.value
		)
		self.assertEqual(
			infer_affected_version_segment_from_msg("style"),
			MutableSegment.MICRO.value
		)
		self.assertEqual(
			infer_affected_version_segment_from_msg("docs"),
			MutableSegment.MICRO.value
		)
		self.assertEqual(
			infer_affected_version_segment_from_msg("refactoring"),
			MutableSegment.MICRO.value
		)
		self.assertEqual(
			infer_affected_version_segment_from_msg("breaking"),
			MutableSegment.MAJOR.value
		)

	def test_infer_affected_version_segment_from_msg_in_sentence(self):
		self.assertEqual(
			infer_affected_version_segment_from_msg("[patch] bla bla bla"),
			MutableSegment.MICRO.value
		)
		self.assertEqual(
			infer_affected_version_segment_from_msg("[prerelease] bla bla bla"),
			MutableSegment.PRE.value
		)
		self.assertEqual(
			infer_affected_version_segment_from_msg("[feature] bla bla bla"),
			MutableSegment.MINOR.value
		)
		self.assertEqual(
			infer_affected_version_segment_from_msg("[breaking] bla bla bla"),
			MutableSegment.MAJOR.value
		)

