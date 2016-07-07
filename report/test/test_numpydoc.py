import unittest

from report.numpydoc import (get_report_from_doc, prepare_docstring,
                             find_sections_in_doc)

try:
    from nilearn.decomposition.canica import CanICA
except ImportError:
    NILEARNTEST = False
else:
    NILEARNTEST = True


DOCSTRING1 = """
This is the documentation for *CanICA 2*

Parameters
----------

param1: (int) to define something

param2: (float ) to define something else

param3: (str) to define another thing

Notes
-----

For example."""

DOCSTRING2 = """
This is the documentation for *CanICA 2*

    Parameters
    ----------

    param1: (int) to define something

    param2: (float ) to define something else

    param3: (str) to define another thing

    Notes
    -----

    For example.
"""


class FindSectionsTC(unittest.TestCase):

    def test_prepare_docstring(self):
        self.assertEqual(DOCSTRING1, prepare_docstring(DOCSTRING2))

    def test_find_title_positions_in_doc(self):
        self.assertListEqual([(43, 64), (183, 194)],
                             find_sections_in_doc(DOCSTRING1))

    def test_find_title_positions_in_doc_with_nilearn(self):
        if not NILEARNTEST:
            self.skipTest('Nilearn is not installed')
        documentation = prepare_docstring(CanICA.__doc__)
        self.assertListEqual([(51, 72), (2633, 2654)],
                             find_sections_in_doc(documentation))

    def test_find_sections(self):
        report = get_report_from_doc(DOCSTRING1)
        report.get_html()


if __name__ == '__main__':
    unittest.main()
