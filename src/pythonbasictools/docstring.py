import inspect
from collections import defaultdict
from copy import deepcopy
from typing import Optional, Union, Type, List, Dict


def get_bases_docs(prop, bases: Optional[Union[Type, List[Type]]] = None) -> Dict[str, str]:
	"""
	Get the docstring of the parent class.
	
	:param prop: The object to find the parent class of.
	:type prop: Any
	:param bases: The list of base classes to inherit the docstring from.
	:type bases: Optional[Union[Type, List[Type]]]
	
	:return: A dictionary of the docstring of the parent class. The key is the name of the parent class and
		the value is the docstring of the parent class.
	:rtype: Dict[str, str]
	"""
	if bases is None:
		raise NotImplementedError(
			"bases cannot be None. In the future, it will be automatically set to the parent class."
		)
	
	if not isinstance(bases, (list, tuple)):
		bases = [bases]
	if inspect.isclass(prop):
		bases = prop.__bases__
		return {b.__name__: inspect.getdoc(b) for b in bases}
	elif inspect.ismethod(prop):
		cls = prop.__self__.__class__
	else:
		self = getattr(prop, "__self__", prop)
		cls = self.__class__
	if bases is None:
		bases = cls.__bases__
	bases_mthds = {base.__name__: getattr(base, prop.__name__, None) for base in bases if base}
	return {k: inspect.getdoc(v) for k, v in bases_mthds.items() if v is not None}


def inherit_docstring(
		_prop=None,
		*,
		sep: str = '\n',
		bases: Optional[Union[Type, List[Type]]] = None
):
	"""
	Decorator to add the docstring of the parent class to the child class.

	:param _prop: The object to decorate.
	:param sep: The separator to use between the docstring of the parent and the child.
	:type sep: str
	:param bases: The list of base classes to inherit the docstring from.
	:type bases: Optional[Union[Type, List[Type]]]

	:return: The decorated object.
	"""
	if bases is None:
		raise NotImplementedError(
			"bases cannot be None. In the future, it will be automatically set to the parent class."
		)
	
	def decorator_func(__prop):
		bases_docs = get_bases_docs(__prop, bases)
		if __prop.__doc__ is None:
			__prop.__doc__ = ""
		__prop.__doc__ = sep.join(filter(None, [d for d in bases_docs.values()])) + sep + inspect.getdoc(__prop)
		return __prop
	
	if _prop is None:
		return decorator_func
	else:
		return decorator_func(_prop)


def inherit_fields_docstring(
		_prop=None,
		*,
		sep: str = '\n',
		bases: Optional[Union[Type, List[Type]]] = None,
		fields: Optional[Union[List[str], str]] = None,
):
	"""
	Inherit the fields of the parents docstrings and add it to the child fields.
	
	:param _prop: The object to decorate.
	:type _prop: Any
	:param sep: The separator to use between the docstring of the parent and the child.
	:type sep: str
	:param bases: The list of base classes to inherit the docstring from.
	:type bases: Optional[Union[Type, List[Type]]]
	:param fields: The list of fields to inherit. If the fields is a string, it will be converted to a list by splitting
		the string by the ',' character. If the fields is None, it will be set to all found fields.
	
	:type fields: Optional[Union[List[str], str]]
	
	:return: The decorated object.
	:rtype: Any
	"""
	if bases is None:
		raise NotImplementedError(
			"bases cannot be None. In the future, it will be automatically set to the parent class."
		)
	if isinstance(fields, str):
		fields = fields.replace(' ', '').split(",")
	
	def decorator_func(__prop):
		new_line_char, new_line_tab_char = '\n', '\n\t\t'
		if __prop.__doc__ is None:
			__prop.__doc__ = ""
		bases_docs = get_bases_docs(__prop, bases)
		if fields is None:
			__prop.__doc__ = sep.join(filter(None, [d for d in bases_docs.values()])) + sep + inspect.getdoc(__prop)
			return __prop
		# bases_fields = {k: walk_docstring(v) for k, v in bases_docs.items()}
		# bases_fields_filtered = {k: {f: v[f] for f in fields if f in v} for k, v in bases_fields.items()}
		bases_fields = {k: {f: get_field_from_docstring(v, f) for f in fields} for k, v in bases_docs.items()}
		self_fields = walk_docstring(inspect.getdoc(__prop))
		doc_wo_fields = deepcopy(inspect.getdoc(__prop))
		for field in fields:
			for subfield in self_fields[field]:
				subfield_doc = format_field(field, subfield)
				doc_wo_fields = doc_wo_fields.replace(subfield_doc, '')
		doc_wo_fields = f"\t{doc_wo_fields.strip()}"
		
		fields_with_self = {**bases_fields, **{__prop.__name__: self_fields}}
		stack_fields = defaultdict(list)
		for cls, cls_fields in fields_with_self.items():
			for field, subfields in cls_fields.items():
				stack_fields[field].extend(subfields)
		joined_fields = {k: sep.join(v) for k, v in stack_fields.items()}
		fields_doc = new_line_char + sep.join([f"\t:{k}:{new_line_char}{v}" for k, v in joined_fields.items()]).replace(
			new_line_char, new_line_tab_char
		)
		__prop.__doc__ = doc_wo_fields + new_line_char + fields_doc
		return __prop
	
	if _prop is None:
		return decorator_func
	else:
		return decorator_func(_prop)


def format_field(field_name: str, field_doc: str) -> str:
	new_line_char, new_line_tab_char = '\n', '\n\t\t'
	if field_name == "Attributes":
		field_doc = field_doc.replace(new_line_char, new_line_tab_char).strip()
		return f"\t:{field_name}:{new_line_tab_char}{field_doc}"
	else:
		raise NotImplementedError(f"Field {field_name} not implemented yet.")


def walk_docstring(doc: str) -> Dict[str, List[str]]:
	from docutils.core import publish_doctree
	import docutils.nodes
	
	doctree = publish_doctree(doc)
	
	class Walker:
		def __init__(self, doc):
			self.document = doc
			self.fields = defaultdict(list)
		
		def dispatch_visit(self, x):
			if isinstance(x, docutils.nodes.field):
				field_name = x.children[0].rawsource
				field_body = x.children[1].rawsource
				self.fields[field_name].append(field_body)
	
	w = Walker(doctree)
	doctree.walk(w)
	return w.fields


def get_field_from_docstring(doc: str, field_name: str) -> List[str]:
	"""
	Get all field body associated to a field name in a docstring.
	
	:param doc: The docstring to parse.
	:type doc: str
	:param field_name: The field name to look for.
	:type field_name: str
	
	:return: The list of field body associated to the field name.
	:rtype: List[str]
	"""
	if field_name == "Attributes":
		return walk_docstring(doc)[field_name]
	else:
		raise NotImplementedError(f"Field {field_name} not implemented yet.")

