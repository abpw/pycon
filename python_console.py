#!/usr/bin/python
# standard libraries
# imports only available in this file
import os, sys
import time, datetime
import functools
from StringIO import StringIO
from code import softspace, InteractiveConsole
from codeop import CommandCompiler
import readline, rlcompleter, atexit, types, subprocess, argparse, imp, __builtin__

# load the library tools used by external function definitions
file_dir = os.path.abspath(os.path.join(os.path.realpath(__file__), os.pardir))
__builtin__.console_lib_tools = imp.load_source('console_lib_tools', os.path.join(file_dir, 'console_lib_tools.py')).export_dict

# find a project-specific console module
# executes "git rev-parse --show-toplevel" to find the project root
#  then looks for a file called console_lib.py
try:
    resp = subprocess.check_output("git rev-parse --show-toplevel", stderr=open(os.devnull, 'w'), shell=True)
    resp = resp.rstrip()
except subprocess.CalledProcessError:
    project_functions = None
except Exception as e:
    raise e
else:
    if os.path.isdir(resp):
        project_functions = imp.load_source('project_functions', os.path.join(resp, 'console_lib.py'))

# import global default and custom functions
default_functions = imp.load_source('default_functions', os.path.join(file_dir, 'default_functions.py'))
try:
    custom_functions = imp.load_source('custom_functions', os.path.join(file_dir, 'custom_functions.py'))
except IOError:
    pass

# inherit the argument parser from project_functions if possible
try:
    parser = project_functions.parser
    parser.description = 'Runs an interactive session after making a bunch of relevant imports.'
except AttributeError:
    # otherwise, try to inherit from custom_functions
    try:
        parser = custom_functions.parser
        parser.description = 'Runs an interactive session after making a bunch of relevant imports.'
    except AttributeError:
        # otherwise, just make a new parser
        parser = argparse.ArgumentParser(description='Runs an interactive session after making a bunch of relevant imports.', add_help=False)
except NameError:
    pass

# checks whether a file can be read or written without opening it
# f is the path to the file
# permission is the permission to be used to open the file
# exists is whether the file needs to already exist or not
# create is whether to create the file if it doesn't exist
#  doesn't do anything if exists=True
def _file_check(f, permission='r', exists=True, create=True):
	if exists and not (os.access(f, os.F_OK) and os.path.isfile(f)):
		raise IOError("[Errno 2] No such file or directory: '%s'" % f)
	if not (exists or os.access(f, os.F_OK)):
		if create:
			with open(f, 'w'):
				pass
		return f
	if 'r' in permission and not os.access(f, os.R_OK):
		raise IOError("[Errno 13] Permission denied: '%s'" % f)
	if 'w' in permission and not os.access(f, os.W_OK):
		raise IOError("[Errno 13] Permission denied: '%s'" % f)
	return f

parser.add_argument('--log', type=functools.partial(_file_check, permission='w', exists=False), default=None,
                    metavar='<log file>', help='Path to a log file. Default is "test_suite.log".')
parser.add_argument('--restart_log', action='store_true', help='Include to wipe the log before saving a log.')
parser.add_argument('--uninstall', action='help', help="Uninstall pycon, but retain custom functions, history, and default log. Must be the first argument.")
parser.add_argument('--purge', action='help', help="Purge pycon. Can't be undone. Must be the first argument.")
parser.add_argument('-h', '--help', action='help', help='Show this help message and exit')

args = parser.parse_known_args()[0]

# class used to wrap stdout and stderror to provide logging
class Out_Stream_Logger():
    def __init__(self, inner, log):
        self.inner = inner
        self.log = log

    def write(self, string):
        self.inner.write(str(string))
        self.log.write(str(string))

    def writelines(self, sequence):
        self.inner.writelines(str(s) for s in sequence)
        self.log.writelines(str(s) for s in sequence)

    def fileno(self):
        return self.inner.fileno()

if args.log:
    log_file = args.log
else:
    log_file = _file_check(os.path.join(file_dir, 'default_output.log'), permission='w', exists=False)

# logic for loading and saving the command history
hist = _file_check(log_file + 'hist', permission='w', exists=False)

def save_history(historyPath=hist):
    import readline
    readline.write_history_file(hist)

if args.restart_log:
    for filename in (log_file, hist):
        with open(filename, 'w') as f:
            f.write('')
else:
    readline.read_history_file(hist)

atexit.register(save_history)

# set up the log file object and bind it as an extra output to stderr
log_file_obj = open(log_file, 'a')
sys.stderr = Out_Stream_Logger(sys.__stderr__, log_file_obj)

# used to provide timestamps on the prompt
class Prompt():
    def __init__(self, suffix):
        self.suffix = suffix
        self.init_time = int(time.time())
        self.prev = None

    def _prev(self):
        return self.prev

    def __str__(self):
        self.prev = '[{:>6d}]{:s}'.format(int(time.time())-self.init_time, self.suffix)
        return self.prev

sys.ps1 = Prompt('> ')
sys.ps2 = Prompt('. ')

# define the starting timestamp
formatted_init = datetime.datetime.utcfromtimestamp(sys.ps1.init_time).strftime('%Y-%m-%d %H:%M:%S')
banner = 'Start time is {:d}: {:s} UTC'.format(sys.ps1.init_time, formatted_init)

class LoggedConsole(InteractiveConsole):
    def __init__(self, locals=None, special_commands={}):
        """Constructor.

        The optional 'locals' argument specifies the dictionary in
        which code will be executed; it defaults to a newly created
        dictionary with key "__name__" set to "__console__" and key
        "__doc__" set to None.

        """
        InteractiveConsole.__init__(self, locals)
        self.special_commands = special_commands
        self.compile = CommandCompiler()

    def runsource(self, source, filename="<input>", symbol="single"):
        try:
            code, context = self.interpert_source(source, filename, symbol)
        except (OverflowError, SyntaxError, ValueError):
            # Case 1
            self.showsyntaxerror(filename)
            return False

        if code is None:
            # Case 2
            return True

        # Case 3
        self.runcode(code, context=context)
        return False

    def runcode(self, code, context=None):
        if not context:
            context = self.locals
        try:
            sys.stdout = Out_Stream_Logger(sys.__stdout__, log_file_obj)
            exec code in context
        except SystemExit:
            raise
        except:
            self.showtraceback()
        else:
            if softspace(sys.stdout, 0):
                print
        finally:
            sys.stdout = sys.__stdout__

    def raw_input(self, prompt=''):
        s = raw_input(str(prompt))
        log_file_obj.write(str(prompt._prev()) + s + '\n')
        return s

    def interpert_source(self, source, filename="<input>", symbol="single"):
        code = str(source)
        if not code:
            return '', self.locals
        if code[0] == "%":
            return 'print shell("{:s}")'.format(code[1:]), self.extended_locals()
        if ' ' in code.lstrip():
            cmd, args = code.lstrip().split(' ', 1)
        elif code.isalnum():
            cmd = code
            args = ''
        else:
            return self.compile(source, filename, symbol), self.locals
        if cmd in special_commands:
            invocation = special_commands[cmd]['invocation']
            code = invocation.format(args)
            return code, self.extended_locals()
        return self.compile(source, filename, symbol), self.locals

    def extended_locals(self):
        extended_locals = dict(self.locals)
        extended_locals.update({f['function'].func_name: f['function'] for f in special_commands.values()})
        return extended_locals

# define and register a function to clear the current log
def clear_log():
    log_file_obj.seek(0,0)
    log_file_obj.truncate()

# console_local_variables is a dictionary of local variables to be passed into the console
console_local_variables = {}
console_local_variables['clear_log'] = clear_log

# register variables and special commands defined in the project and default files
special_commands = {}
for module in ('default_functions', 'custom_functions', 'project_functions'):
    if module not in vars() or not vars()[module]:
        continue
    module = vars()[module]
    for var in module.export_dict:
        if var == '~special_commands':
            for command in module.export_dict[var]:
                special_commands[command] = module.export_dict[var][command]
        else:
            console_local_variables[var] = module.export_dict[var]

# start the interperter with console features
readline.set_completer(rlcompleter.Completer(console_local_variables).complete)
readline.parse_and_bind("tab: complete")
LoggedConsole(locals=console_local_variables, special_commands=special_commands).interact(banner=banner)

exit()
