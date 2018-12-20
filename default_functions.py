# File containing default special functions
# these four lines import the registration decorators and functions
import __builtin__
assert hasattr(__builtin__, 'console_lib_tools'), 'No console tools found'
for tool in __builtin__.console_lib_tools:
    vars()[tool] = __builtin__.console_lib_tools[tool]

# modules used by this file
from os import chdir
import inspect
from pprint import pprint
from subprocess import Popen, CalledProcessError, PIPE

# registers useful modules
useful_mods = ('os',
               'sys',
               'random',
               'inspect',
               'pdb',
               'time',
               'datetime',
               'functools',
               'json'
               )
register_modules(*useful_mods)

# register the pprint function as a variable since we don't have access to its source
register_variables(pprint=pprint)

description = 'Execute arbitrary non-interactive commands in the shell. Also invoked by starting a line with "%", in which case the response is printed'
detail_dict = {'Parameter:': {'<command>': 'A string to be executed in the shell'}, 'Returns:': {'<output>': 'The output, including errors, of the command executed, as a string'}}
# executes arbitrary non-interactive commands in the shell
# also called by starting an input line with '%', in which case the response is printed
@register_function(description, detail_dict=detail_dict)
def shell(command):
    try:
        pipe = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
        response = pipe.communicate()
        resp = response[0]
        if response[1]:
            resp += '"{:s}" produced the following error:\n'.format(command)
            resp += str(response[1])
    except CalledProcessError as e:
        resp = '"{:s}" produced the following error:\n'.format(e.cmd)
        resp += str(e.output)
    except Exception as e:
        resp = str(e)
    finally:
        return resp.rstrip()

description = 'Pretty print a value.'
detail_dict = ['Usage: "pp <value>"', {'Parameter:': {'<value>': 'A value or object to be pretty printed, as with pprint() from the pprint module.'}}]
@register_command('pp', description=description, detail_dict=detail_dict)
def pretty_print(obj):
    pprint(obj)

@register_command('exit', help=False)
@register_command('quit', help=False)
@register_command('q', description='Quit the console.')
def quit_console(*args):
    exit()

description = 'Change the current working directory. Takes an absolute or relative path as a parameter.'
detail_dict = ['Usage: "cd <path>"', {'Parameter:': {'<path>': 'Absolute or relative path to which to change the current working directory.'}}]
@register_command('cd', invocation='change_directory("{:s}")', description=description, detail_dict=detail_dict)
def change_directory(path):
    os.chdir(path)

@register_command('members', description='Print the member attributes of the argument object.')
def print_members(object):
    pprint(inspect.getmembers(object))

@register_command('methods', description="Print the bound methods of the argument object.")
def print_methods(object):
    pprint([memb for memb in inspect.getmembers(object) if 'bound method' in memb[1])

detail_dict = ['Usage: "help[ <query 1>[ <query 2>[ <query 3>...]]]"',
               {'Parameters:':
                    {'<query>':
                        "A built-in function or command you'd like more info on. Any number of these can be included. If none, prints help for all functions and commands with help entries."}}]
@register_command('help', description='Print this message ;). Also optionally can be used for information on certain commands', detail_dict=detail_dict, invocation='print_help("{:s}")')
@register_command('h', help=False, invocation='print_help("{:s}")')
def print_help(*args):
    if not args:
        output = 'This is the extensible interactive console. These are the special commands and\n objects that have descriptions defined.\n\n'
        entries = help_function_info
    else:
        output = ''
        args = args[0].split()
        entries = {key: help_function_info[key] for key in args if key in help_function_info}
        def default_dict(obj_name):
            return {'signature': "There's no help entry for '{:s}'".format(obj_name),
                    'description': '',
                    'detail_dict': {}}
        entries.update({key: default_dict(key) for key in args if key not in help_function_info})
    def create_strings(indent, obj):
        if type(obj) == type(''):
            strings = obj.split('\n')
            line_len = 80 - 2 * indent
            new_strings = ''
            for string in strings:
                while string:
                    if len(string) == 0:
                        break
                    elif len(string) <= line_len:
                        new_strings += '  ' * indent + string.rstrip() + '\n'
                        break
                    else:
                        string = string.lstrip()
                        last_index = string.rfind(' ', 0, line_len)
                        new_strings += '  ' * indent + string[:last_index].rstrip() + '\n'
                        string = string[last_index:].lstrip()
            strings = new_strings
        elif type(obj) == type({}):
            strings = ''
            for key in obj:
                strings += create_strings(indent, key)
                strings += create_strings(indent + 1, obj[key])
        elif type(obj) == type([]):
            strings = ''
            for entry in obj:
                strings += create_strings(indent, entry)
        else:
            raise TypeError('detail_dict must be a dictionary of nested dicts/lists/strings')
        return strings
    for entry in entries:
        signature = '{:s} - {:s}\n'.format(entry, entries[entry]['signature'])
        if len(signature) > 80:
            line_len = 80
            new_signature = ''
            while signature:
                last_index = signature.rfind(' ', 0, line_len)
                new_signature += ' ' * int(line_len != 80) + signature[:last_index].rstrip() + '\n'
                signature = signature[last_index:].lstrip()
                line_len = 79
            signature = new_signature
        output += signature
        output += create_strings(1, entries[entry]['description'])
        output += create_strings(1, entries[entry]['detail_dict'])
        output += '\n'
    print output.rstrip()
