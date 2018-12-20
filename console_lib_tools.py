# file that defines tools available to all functions that define special function files
# through some magic hackery, this doesn't need to be imported directly into those files
#  instead, any variable with an entry in "export_dict" by the end of execution will be available
#  by default, this is all imported modules and all functions, defined locally or imported
# these functions execute in the namespace local to this file, so to modify the export_dict
#  of a special functions file, "export_dict['export_dict']" can be used as a reference
import importlib

export_dict = {}
export_dict['export_dict'] = {'~special_commands': {}}
export_dict['help_function_info'] = {}

# internal function for registering a tool to be exported to
# optionally takes a description of the function as a parameter
def _register_lib_tool(input):
    description = ''
    call = True
    if not callable(input):
        call = False
        description = input
    def registration_decorator(func):
        # todo: deal with descriptions
        export_dict[func.func_name] = func
        return func
    if call:
        return registration_decorator(input)
    return registration_decorator

# store description of a registered object for the help function
# the arguments are handled by the "print_help()" function (the "help" command)
# which is defined in "default_functions.py"
def _store_help(name, signature, description, detail_dict={}):
    export_dict['help_function_info'][name] = {'signature': signature,
                                                'description': description,
                                                'detail_dict': detail_dict}

# decorator for registering functions to be available in the console's namespace
# optionally, the input is a string that describes the function, with keyword arguments
# describing the arguments to the function.
@_register_lib_tool
def register_function(input, detail_dict={}, help=True):
    if callable(input):
        export_dict['export_dict'][input.func_name] = input
        return input
    else:
        def registration_decorator(func):
            if help:
                _store_help(func.func_name, 'python function', input, detail_dict=detail_dict)
            export_dict['export_dict'][func.func_name] = func
            return func
        return registration_decorator

# decorator for registering commands to be available in the console's namespace
# command is the base command to be entered into the console by the user, like 'cd' or 'pp'
# invocation is how the interpreter invokes the function
#  the default, for example, is '<func>({:s})', where <func> is the name of the python function
#   being invoked, and {:s} will be replaced by the arguments to the command
@_register_lib_tool
def register_command(command, invocation=None, description='', detail_dict={}, help=True):
    if help:
        _store_help(command, 'special command', description, detail_dict)
    if invocation:
        def registration_decorator(func):
            export_dict['export_dict']['~special_commands'][command] = {'function': func, 'invocation': invocation}
            return func
        return registration_decorator
    def registration_decorator(func):
        invocation = '{:s}({:s})'.format(func.func_name, '{:s}')
        export_dict['export_dict']['~special_commands'][command] = {'function': func, 'invocation': invocation}
        return func
    return registration_decorator

# function for registering variables
# for example, calling "register_variables(foo=3, bar='test')"
#  will make a variable foo with value 3 and a variable bar with value 'test',
#  both available in the console upon startup
@_register_lib_tool
def register_variables(**vars):
    for var in vars:
        export_dict['export_dict'][var] = vars[var]

# function for registering modules
# takes any number of arguments as strings of the names of the modules to be registered
# or keyword arguments such that the argument foo='bar' imports the foo module as bar
# also optionally takes a dictionary 'partials' of module names to the names of one or
#  more desired attributes to import, as strings or an iterable of strings
@_register_lib_tool
def register_modules(*mods, **renamed_mods):
    for mod in mods:
        export_dict['export_dict'][mod] = importlib.import_module(mod)
    for mod in renamed_mods:
        if mod != 'partials':
            export_dict['export_dict'][renamed_mods[mod]] = importlib.import_module(mod)
    partials = renamed_mods.get('partials', {})
    for mod in partials:
        module = importlib.import_module(mod)
        def import_partial(obj):
            if obj == '*':
                attrs = [attr for attr in module.__all__]
            elif type(obj) == type(''):
                attrs = [obj]
            elif hasattr(obj, '__iter__'):
                for sub_obj in obj:
                    import_partial(sub_obj)
                return
            else:
                raise TypeError('The desired attributes must be specified as strings or iterables thereof')
            for attr in attrs:
                export_dict['export_dict'][attr] = getattr(module, attr)
        import_partial(partials[mod])
