# pycon
## a customizable interactive python 2 console with some bash functionality

To pagkage from source, execute "./package.sh"

To install, after packaging, execute "./install_pycon.sh"

For other information, execute "pycon -h" after installation.

For information about the special commands, execute "help" from inside pycon.



To add custom commands or functions, write and decorate functions in ~/.pycon/custom_functions.py

To add custom modules or objects, use the register_modules() or register_variables() functions, described below, respectively.

See ~/.pycon/default_functions.py for examples of how to register modules, commands, and functions.

Customizations can also be defined on a per-project basis by defining a console_lib.py file of the same format as custom_functions.py/default_functions.py in the root of your git project. These customizations will only be available if pycon is executed from within that git project.



### The available registration functions/decorators are:
#### @register_command(<command>, invocation=None, description='', detail_dict={}, help=True)
##### decorator for registering commands to be available in the console's namespace
* command is the base command to be entered into the console by the user, like 'cd' or 'pp'
* invocation is how the interpreter invokes the function 
  * the default, for example, is '<func>({:s})', where <func> is the name of the python function being invoked, and {:s} will be replaced by the arguments to the command
* the other arguments deal with how the command will be described by the help command:
  * description is a description of the command
  * detail_dict can contain hierarchical information about the command, like a description of arguments
  * help is whether to include a help entry for the command

#### @register_function(description='', detail_dict={}, help=True)
##### decorator for registering functions to be available in the console's namespace
* the arguments deal with how the command will be described by the help command:
  * description is a description of the function
  * detail_dict can contain hierarchical information about the function, like a description of arguments
  * help is whether to include a help entry for the function

#### register_variables(\*\*vars)
##### function for registering variables
For example, calling "register_variables(foo=3, bar='test')" will make a variable foo with value 3 and a variable bar with value 'test', both available in the console upon startup

#### register_modules(partials={}, \*mods, \*\*renamed_mods)
##### function for registering modules
Takes any number of arguments as strings of the names of the modules to be registered or keyword arguments such that the argument foo='bar' imports the foo module as bar
 
Also optionally takes a dictionary 'partials' of module names to the names of one or more desired attributes to import, as strings or an iterable of strings
