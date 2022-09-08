import inspect
from collections import defaultdict
from copy import deepcopy
from typing import Optional, Union, Type, List, Dict
from docutils.core import publish_doctree
import docutils.nodes


def get_bases_docs(prop, bases: Optional[Union[Type, List[Type]]] = None) -> Dict[str, str]:
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
	def decorator_func(__prop):
		bases_docs = get_bases_docs(__prop, bases)
		# print(f"{inspect.isfunction(__prop) = }, {inspect.ismethod(__prop) = }, {inspect.isclass(__prop) = }")
		# print(f"{__prop}")
		# print(f"{__prop.__name__}({cls}).bases = {__bases}")
		if __prop.__doc__ is None:
			__prop.__doc__ = ""
		__prop.__doc__ = sep.join(filter(None, [d for d in bases_docs.values()])) + __prop.__doc__
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
		fields: Optional[List[str]] = None,
):
	def decorator_func(__prop):
		new_line_char, new_line_tab_char = '\n', '\n\t\t'
		if __prop.__doc__ is None:
			__prop.__doc__ = ""
		bases_docs = get_bases_docs(__prop, bases)
		if fields is None:
			__prop.__doc__ = sep.join(filter(None, [d for d in bases_docs.values()])) + __prop.__doc__
			return __prop
		# bases_fields = {k: walk_docstring(v) for k, v in bases_docs.items()}
		# bases_fields_filtered = {k: {f: v[f] for f in fields if f in v} for k, v in bases_fields.items()}
		bases_fields = {k: {f: get_field_from_docstring(v, f) for f in fields} for k, v in bases_docs.items()}
		self_fields = walk_docstring(__prop.__doc__)
		doc_wo_fields = deepcopy(__prop.__doc__)
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
	if field_name == "Attributes":
		return walk_docstring(doc)[field_name]
	else:
		raise NotImplementedError(f"Field {field_name} not implemented yet.")
