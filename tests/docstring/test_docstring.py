import unittest
import pythonbasictools as pbt


class Mock:
	"""
	This is a mock docstring.
	
	:Attributes:
		- :attr:`attr1` (int): this is attr1
		- :attr:`attr2` (int): this is attr2
		- :attr:`attr3` (int): this is attr3
	"""
	
	def __init__(self, param1: int, param2: int, param3: int):
		"""
		This is the init docstring.
		
		:param param1: this is param1
		:type param1: int
		:param param2: this is param2
		:type param2: int
		:param param3: this is param3
		:type param3: int
		"""
		self.attr1 = 1
		self.attr2 = 2
		self.attr3 = 3


class TestDocstring(unittest.TestCase):
	def test_docstring(self):
		doc = pbt.docstring.get_field_from_docstring(Mock.__doc__, "Attributes")
		self.assertTrue(all(
			[doc[i] == s for i, s in enumerate([
				"- :attr:`attr1` (int): this is attr1\n"
				"- :attr:`attr2` (int): this is attr2\n"
				"- :attr:`attr3` (int): this is attr3\n"
			])]))






