from subprocess import call
from os import unlink, mkdir

python_module_template = """from setuptools import setup
from pybind11.setup_helpers import Pybind11Extension, build_ext
from pybind11 import get_cmake_dir

import sys

__version__ = "0.0.1"
"""

def c_compile(source, output, shared = True, python_module = False, **py_module_args):
    if not python_module:
        open("temp.cpp", mode="w+").write(str(source))
        call(["gcc", "temp.cpp", "-o", str(output)])
    else:
        try:
            mkdir(output)
        except:
            pass

        open(f"{output}/{output}.cpp", mode="w+").write(source.get_as_module(output))
        setup_py = python_module_template
        args = ""

        for (key, val) in py_module_args.items():
            args += f"{key}={val},\n"

        args += "cmdclass={\"build_ext\": build_ext},\n"
        args += "ext_modules=ext_modules,\n"

        setup_py += f"""ext_modules = [
Pybind11Extension("{output}",
["{output}.cpp"],
# Example: passing in the version to the compiled code
define_macros = [('VERSION_INFO', __version__)],
),
]

setup(
name="{output}", 
{args}
)"""    
        open(f"{output}/setup.py", mode="w+").write(setup_py)
    # unlink("temp.cpp")
        