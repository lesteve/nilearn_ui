import unittest

from scripts import (registered_script_description,
                     _find_parameters_section,
                     _parse_parameters_section,
                     _parse_computation_title,
                     description_from_docstring)

DOCSTRING = """
CanICA

Parameters
----------

param1: (10) param1 description

param2: (3.14) param2 is an approximation of pi

param3: (folder) You must specified a folder

Notes
-----

For example."""


class RegistrationTC(unittest.TestCase):

    def test_registered_script(self):
        d = registered_script_description()


class DescriptionFromDocstring(unittest.TestCase):
    def test_find_parameters(self):
        parameters = _find_parameters_section(DOCSTRING)
        self.assertEqual(DOCSTRING[
            DOCSTRING.find('\nparam1'):DOCSTRING.find('Notes')],
                         parameters)

    def test_parse_parameters_section(self):
        parameters = _find_parameters_section(DOCSTRING)
        params = _parse_parameters_section(parameters)
        self.assertListEqual([('param1', 10,),
                               # 'param1 description'),
                              ('param2', 3.14,),
                               # 'param2 is an approximation of pi'),
                              ('param3', '%folder_picker',),
                               #'You must specified a folder')
                               ],
                             params)

    def test_parse_computation_title(self):
        self.assertEqual(_parse_computation_title(DOCSTRING),
                         'CanICA')


if __name__ == '__main__':
    unittest.main()
