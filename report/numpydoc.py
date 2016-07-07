"""
This module contains helper function to convert a numpy like docstring
into valid html.

This module use nilearn_ui report API
"""

import re
import itertools

from docutils import core
from docutils.writers.html4css1 import Writer, HTMLTranslator

from report import report_api as api

from scipy.misc.doccer import unindent_string


class NoHeaderHTMLTranslator(HTMLTranslator):
    def __init__(self, document):
        HTMLTranslator.__init__(self, document)
        self.head_prefix = ['', '', '', '', '']
        self.body_prefix = []
        self.body_suffix = []
        self.stylesheet = []


_WRITER = Writer()
_WRITER.translator_class = NoHeaderHTMLTranslator


def section_to_html(section):
    """convert section content into html"""
    return '\n'.join(core.publish_string(section,
                                         writer=_WRITER).split('\n')[10:-2])


def find_sections_in_doc(documentation):
    """documentation is a string containing a docstring
    formatting like numpy documentation. "find_title_positions_in_doc"
    return a list of tuple position where restructured text
    title can be found"""
    section_re = re.compile(r"[\w ]*\n-{3,}")
    positions = [(m.start(), m.end())
                 for m in section_re.finditer(documentation)]
    return positions


def prepare_docstring(documentation):
    """prepare numpy documentation to find section analysis.
    numpy documentation must not have indentation
    """
    first_indentation = documentation.find('\n ')
    if first_indentation != -1:
        return (documentation[: first_indentation]
                + unindent_string(documentation[first_indentation:]))
    return unindent_string(documentation)


def get_report_from_doc(documentation):
    """
    return a report object generated from a docstring (documentation)
    the docstring is expected to follow numpy documentation format
    """
    documentation = prepare_docstring(documentation)
    positions = find_sections_in_doc(documentation)
    report = api.Report()
    section = api.Section('Description')
    report.add(section)
    if not positions:
        if documentation:
            section.add(api.Paragraph(documentation))
        else:
            section.add(api.Paragraph("No documentation"))
        return report
    end_description = positions[0][0]
    if documentation[:end_description].strip():
        section.add(api.Paragraph(
            section_to_html(documentation[:end_description])))
    start_positions = list(itertools.chain(*positions))
    end_positions = start_positions[1:] + [len(documentation)]
    for i, (start, end) in enumerate(zip(start_positions, end_positions)):
        if i%2:
            section.add(api.Paragraph(
                section_to_html(documentation[start:end])))
        else:
            title = documentation[start: end].split('\n')[0]
            section = api.Section(title)
            report.add(section)
    return report

