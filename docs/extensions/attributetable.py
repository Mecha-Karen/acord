"""
Majority of code used, was used from discord.py.

SOURCE: https://github.com/rapptz/discord.py/
"""

from collections import OrderedDict, namedtuple
import importlib
import inspect
import re

# Sphinx imports
from sphinx.util.docutils import SphinxDirective
from sphinx.locale import _
from docutils import nodes
from sphinx import addnodes


class AttrTable(nodes.General, nodes.Element):
    pass

class AttrTableColumn(nodes.General, nodes.Element):
    pass

class AttrTableTitle(nodes.TextElement):
    pass

class AttrTablePlaceHolder(nodes.General, nodes.Element):
    pass

class AttrTableBadge(nodes.TextElement):
    pass

class AttrTableItem(nodes.Part, nodes.Element):
    pass


def visit_AttrTable_node(self, node):
    class_ = node["python-class"]
    self.body.append(f'<div class="py-attribute-table" data-move-to-id="{class_}">')


def visit_AttrTableColumn_node(self, node):
    self.body.append(self.starttag(node, 'div', CLASS='py-attribute-table-column'))


def visit_AttrTableTitle_node(self, node):
    self.body.append(self.starttag(node, 'span'))


def visit_AttrTableBadge_node(self, node):
    attributes = {
        'class': 'py-attribute-table-badge',
        'title': node['badge-type'],
    }
    self.body.append(self.starttag(node, 'span', **attributes))


def visit_AttrTableItem_node(self, node):
    self.body.append(self.starttag(node, 'li', CLASS='py-attribute-table-entry'))


def depart_AttrTable_node(self, node):
    self.body.append('</div>')


def depart_AttrTableColumn_node(self, node):
    self.body.append('</div>')


def depart_AttrTableTitle_node(self, node):
    self.body.append('</span>')


def depart_AttrTableBadge_node(self, node):
    self.body.append('</span>')


def depart_AttrTableItem_node(self, node):
    self.body.append('</li>')


_name_parser_regex = re.compile(r'(?P<module>[\w.]+\.)?(?P<name>\w+)')


class PyAttrTable(SphinxDirective):
    has_content = False
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {}

    def parse_name(self, content):
        path, name = _name_parser_regex.match(content).groups()
        if path:
            modulename = path.rstrip('.')
        else:
            modulename = self.env.temp_data.get('autodoc:module')
            if not modulename:
                modulename = self.env.ref_context.get('py:module')
        if modulename is None:
            raise RuntimeError('modulename somehow None for %s in %s.' % (content, self.env.docname))

        return modulename, name

    def run(self):
        content = self.arguments[0].strip()
        node = AttrTablePlaceHolder('')
        modulename, name = self.parse_name(content)
        node['python-doc'] = self.env.docname
        node['python-module'] = modulename
        node['python-class'] = name
        node['python-full-name'] = f'{modulename}.{name}'
        return [node]

def build_lookup_table(env):
    # Given an environment, load up a lookup table of
    # full-class-name: objects
    result = {}
    domain = env.domains['py']

    ignored = {
        'data', 'exception', 'module', 'class',
    }

    for (fullname, _, objtype, docname, _, _) in domain.get_objects():
        if objtype in ignored:
            continue

        classname, _, child = fullname.rpartition('.')
        try:
            result[classname].append(child)
        except KeyError:
            result[classname] = [child]

    return result


TableElement = namedtuple('TableElement', 'fullname label badge')

def process_AttrTable(app, doctree, fromdocname):
    env = app.builder.env

    lookup = build_lookup_table(env)
    for node in doctree.traverse(AttrTablePlaceHolder):
        modulename, classname, fullname = node['python-module'], node['python-class'], node['python-full-name']
        groups = get_class_results(lookup, modulename, classname, fullname)
        table = AttrTable('')
        for label, subitems in groups.items():
            if not subitems:
                continue
            table.append(class_results_to_node(label, sorted(subitems, key=lambda c: c.label)))

        table['python-class'] = fullname

        if not table:
            node.replace_self([])
        else:
            node.replace_self([table])

def get_class_results(lookup, modulename, name, fullname):
    module = importlib.import_module(modulename)
    cls = getattr(module, name)

    groups = OrderedDict([
        (_('Attributes'), []),
        (_('Methods'), []),
    ])

    try:
        members = lookup[fullname]
    except KeyError:
        return groups

    for attr in members:
        attrlookup = f'{fullname}.{attr}'
        key = _('Attributes')
        badge = None
        label = attr
        value = None

        for base in cls.__mro__:
            value = base.__dict__.get(attr)
            if value is not None:
                break

        if value is not None:
            doc = value.__doc__ or ''
            if inspect.iscoroutinefunction(value) or doc.startswith('|coro|'):
                key = _('Methods')
                badge = AttrTableBadge('async', 'async')
                badge['badge-type'] = _('coroutine')
            elif isinstance(value, classmethod):
                key = _('Methods')
                label = f'{name}.{attr}'
                badge = AttrTableBadge('cls', 'cls')
                badge['badge-type'] = _('classmethod')
            elif inspect.isfunction(value):
                if doc.startswith(('A decorator', 'A shortcut decorator')):
                    # finicky but surprisingly consistent
                    badge = AttrTableBadge('@', '@')
                    badge['badge-type'] = _('decorator')
                    key = _('Methods')
                else:
                    key = _('Methods')
                    badge = AttrTableBadge('def', 'def')
                    badge['badge-type'] = _('method')

        groups[key].append(TableElement(fullname=attrlookup, label=label, badge=badge))

    return groups

def class_results_to_node(key, elements):
    title = AttrTableTitle(key, key)
    ul = nodes.bullet_list(style="list-style: none;")
    for element in elements:
        ref = nodes.reference('', '', internal=True,
                                      refuri='#' + element.fullname,
                                      anchorname='',
                                      *[nodes.Text(element.label)])
        para = addnodes.compact_paragraph('', '', ref)
        if element.badge is not None:
            ul.append(AttrTableItem('', element.badge, para))
        else:
            ul.append(AttrTableItem('', para))

    return AttrTableColumn('', title, ul)

def setup(app):
    app.add_directive('attributetable', PyAttrTable)
    app.add_node(AttrTable, html=(visit_AttrTable_node, depart_AttrTable_node))
    app.add_node(AttrTableColumn, html=(visit_AttrTableColumn_node, depart_AttrTableColumn_node))
    app.add_node(AttrTableTitle, html=(visit_AttrTableTitle_node, depart_AttrTableTitle_node))
    app.add_node(AttrTableBadge, html=(visit_AttrTableBadge_node, depart_AttrTableBadge_node))
    app.add_node(AttrTableItem, html=(visit_AttrTableItem_node, depart_AttrTableItem_node))
    app.add_node(AttrTablePlaceHolder)
    app.connect('doctree-resolved', process_AttrTable)
