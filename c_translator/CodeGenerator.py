from abc import abstractmethod
from typing import List

class Line:
    line = []

    def __init__(self, line: List):
        self.line = line

    def add(self, line):
        self.line.append(line)

    def set_to(self, index, value):
        self.line[index] = value

    def new_line(self, value):
        self.line = value

    def get(self, start, end = None):
        end = end if end else len(self.line)

        return self.line[start:end]

    @property
    def length(self):
        return len(self.line)

    def get_line(self):
        return self.line

class Closer:

    instances = []

    @property
    def functions(self):
        functions = []
        for instance in self.instances:
            functions.append({
                "name": instance.target.name,
                "args": instance.target.args,
                "body": instance.get_body()
            })
        return functions

    def add(self, instance_close):
        self.instances.append(instance_close)

    def __call__(self):
        for instance in self.instances:
            if not instance.closed:
                instance.close()

class c_env:

    lines: list[Line] = []
    closer = Closer()

    def add_block(self, block):
        self.closer.add(block)

    def get_as_module(self, name):
        link_line = self.lines[0].get(0)
        link_line.insert(0, "#include<pybind11/pybind11.h>\n#define STRINGIFY(x) #x\n#define MACRO_STRINGIFY(x) STRINGIFY(x)\nnamespace py = pybind11;")
        self.lines[0].new_line(link_line)

        module_line = self.add_line([""])
        module_line.add(f"PYBIND11_MODULE({name}, m)")
        module_line.add("{")

        for function in self.closer.functions:
            module_line.add(f"m.def(\"{function['name']}\", &{function['name']}, \"This function created by c_translator module\");")

        module_line.add("#ifdef VERSION_INFO\nm.attr(\"__version__\") = MACRO_STRINGIFY(VERSION_INFO);\n#else\nm.attr(\"__version__\") = \"dev\";\n#endif\n}")
        return str(self)

    def add_line(self, line):
        self.lines.append(Line(line))
        return self.lines[len(self.lines) - 1]
        # return self.

    def test(self):
        print(self.closer.functions)

    def __str__(self):
        return_line = ""
        self.closer()
        for line in self.lines:
            if isinstance(line, Line): 
                return_line += "\n".join(line.get_line())
            else:
                return_line += line
        return return_line

class c_type:
    @property
    @abstractmethod
    def typ(self):
        pass

    @property
    @abstractmethod
    def value(self):
        pass

class c_int(c_type):

    def __init__(self):
        pass

    def __repr__(self):
        return self.typ

    @property
    def typ(self):
        return "int"

    def __call__(self, value):
        return c_value(self.typ, value)

class c_value:
    def __init__(self, typ, value):
        self.typ = typ
        self.value = value

    def __repr__(self):
        return self.typ + " " + str(self.value)

class _c_argument:
    def __init__(self, name: str, typ: c_type, default_value = None):
        self.name = name
        self.type = typ

        if default_value:
            self.default_value = default_value

class _c_arguments:
    def __init__(self, args):
        self.args = [_c_argument(str(i), arg) for i, arg in enumerate(args)]

    def __getitem__(self, index):
        return self.args[index]

    def get_line(self):
        return_value = ""
        for arg in self.args:
            return_value += f"{arg.type.typ} {arg.name}"

        return return_value

class c_function:
    def __init__(self, name: str, typ: c_type, args: List[c_type]): 
        self.name = name
        self.type = typ
        self.args = _c_arguments(args)

    def get_line(self):
        return f"{self.type.typ} {self.name} ({self.args.get_line()})"

class c_void(c_type):
    
    @property
    def typ(self):
        return "void"

class c_struct:
    def append(self):
        pass

class c_enum(c_struct):
    pass

class c_builder:

    line: Line

    def __init__(self, module: c_env, target = None):
        self.mod = module
        self.closed = False
        self.line = self.mod.add_line([])
        self.variables = []
        self.mod.add_block(self)

        if isinstance(target, c_function):
            self.target = target
            self.line.add(target.get_line())
        else:
            main = c_function("main", c_void(), [])
            self.target = main
            self.line.add(f"{main.type.typ} {main.name} ()")

        for arg in self.target.args:
            self.variables.append(arg.name)

        self.line.add("{")

    def ret(self):
        pass

    def get_body(self):
        return self.line.get(2, self.line.length - 1)

    def assign(self, name: str, value: c_value):
        if not self.closed:
            if name not in self.variables:
                self.line.add(f"{value.typ} {name} = {value.value};")
                return _c_func_variable(name)

            self.variables.append(name)
            self.line.add(f"{name} = {value.value};")
            return _c_func_variable(name)

    def ret(self, value):
        self.line.add(f"return {value.get_line()};")

    def ret_void(self):
        self.line.add("return;")

    def if_then(self, comp):
        return _c_if_then(self, comp)

    def func_call(self, fn, args): 
        pass

    def close(self):
        self.line.add("}")
        self.closed = True

class _c_func_variable:
    def __init__(self, name):
        self.name = name

    def get_line(self):
        return self.name

class _c_if_then:

    def __init__(self, builder: c_builder, comparation):
        self.builder = builder
        self.comparation = comparation

    def __enter__(self):
        self.builder.line.add(f"if ({self.comparation}) " + "{")

    def __exit__(self, type, value, traceback):
        self.builder.line.add("}")

class c_class:
    pass
#     def __init__(self, name):
#         self.name = name
