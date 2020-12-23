# c_translator
Binding for creating c++-like code

This module allows you to create and compile c-like code

The api from llvmlite was taken as a basis

## Examples
### Generating code
```python
from c_translator import CodeGenerator as ir # CodeGenerator imports as ir 
from c_translator.compile import c_compile # Compiler to bytecode

# Creating env(as module in llvmlite)
mod = ir.c_env()

# 1 - name, 2 - return type, 3 - function argument types 
fy_inst = ir.c_function("test", ir.c_int(), [ir.c_int()])
fy_inst.args[0].name = "argument" # setting name of argument of function, default is index in order

builder = ir.c_builder(mod, fy_inst) # function builder

# 1 - variable name, 2 - value
assign_variable = builder.assign("assign_variable", ir.c_int()(10)) # assign variable

# comparsion
with builder.if_then("1 < 2"): 
    builder.assign("any_in_comp", ir.c_int()(10))

# return value
builder.ret(assign_variable)

c_compile(
    source=mod, 
    output="test", 
    )
```

start this code and module automatic generate compiled to bytecode file by g++

## Futures
- [ ] Add code generating classes
- [ ] Add support for compiling to node native addons
- [ ] create OOP adaptive comp
