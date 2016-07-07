
import os.path as osp
import importlib
import re

from glob import glob

from report.numpydoc import prepare_docstring, find_sections_in_doc


class NilearnUiDocStringError(Exception):
    pass


PARAMETER_LINE = re.compile(r'(\w+):[ ]+\(([\w.]+)\)[ ]+([\w ]*)')

TO_FORMLAYOUT_KEY = {'folder': 'dir'}

def _script_path():
    return osp.dirname(__file__)


def registered_script_description():
    description, functions = {}, {}
    for script_name in glob(osp.join(_script_path(), 'run_*.py')):
        module_name = osp.basename(script_name)[:-3]
        module_path = 'scripts.%s' % module_name
        module = importlib.import_module(module_path, 'scripts')
        function = getattr(module, module_name)
        title, params = description_from_docstring(function)
        description[title] = params
        functions[title] = function
    return description, functions


def _find_parameters_section(docstring):
    parameter_start = None
    for start, end in find_sections_in_doc(docstring):
        if parameter_start is not None:
            return docstring[parameter_start:start]
        if docstring[start:(start+end)/2] == 'Parameters':
            parameter_start = end + 1
    if parameter_start is not None:
        return  docstring[parameter_start:]
    else:
        import pdb;pdb.set_trace()
        raise NilearnUiDocStringError


def _convert_default_value(value):
    try:
        value = eval(value)
    except:
        pass # it is a string
    return TO_FORMLAYOUT_KEY.get(value, value)


def _parse_parameters_section(parameters):
    parameter_list = []
    for line in parameters.splitlines():
        m = PARAMETER_LINE.match(line)
        if m:
            parameter_list.append(
                ('%s::%s' % (m.group(1), m.group(3)),
                 _convert_default_value(m.group(2))))
    return parameter_list


def _parse_computation_title(docstring):
    for line in docstring.splitlines():
        if line:
            return line


def description_from_docstring(function):
    """parse docstring parameters description to generate
    a dictionnary for formlayout
    """
    docstring = prepare_docstring(function.__doc__)
    title = _parse_computation_title(docstring)
    parameters = _find_parameters_section(docstring)
    params = _parse_parameters_section(parameters)
    return title, params

COMPUTATIONS, FUNCTIONS = registered_script_description()

