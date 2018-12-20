# File containing custom special functions
# See default_functions.py for an example of how to add custom functions
# or commands

# these four lines import the decorators
import __builtin__
assert hasattr(__builtin__, 'console_lib_tools'), 'No console tools found'
for tool in __builtin__.console_lib_tools:
    vars()[tool] = __builtin__.console_lib_tools[tool]
