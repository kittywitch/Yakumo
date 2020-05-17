import logging, os, inspect, imp, re

global base_path
global actions
actions = {}

# this function checks for files with ".py" in the directory, then adds them to a list
def modules_in_dir(path):
	result = set()
	for entry in os.listdir(path):
		if os.path.isfile(os.path.join(path, entry)):
			matches = re.search("(.+\.py)$", entry)
			if matches:
				result.add(matches.group(0))
	return result

# this function uses imp.load_module to load those files somewhat manually, but, providing a wildcard import for a dir
def import_dir(path):
	for filename in sorted(modules_in_dir(path)):
		search_path = os.path.join(os.getcwd(), path)
		module_name, ext = os.path.splitext(filename)
		fp, path_name, description = imp.find_module(module_name, [search_path,])
		module = imp.load_module(module_name, fp, path_name, description)
 
 # - - - - - - - - - - - - - 
# Modular Action System 
# - - - - - - - - - - - - -

# this is used as a decorator within the actions/ folders.
# it adds a key value pair to actions, where the key => the name of the action, value => the function that corresponds to it
# example:
# @components.modularity.add("hello_world")
# def hello_world(data, server):
#   pass
def add(name):
	frame = inspect.stack()[1]
	filename = os.path.relpath(frame[0].f_code.co_filename, base_path)
	def wrapper(function):
		actions[name] = function
		logging.info(f"Loaded action \"{function}\" as \"{name}\" from \"{filename}\".")
		return function
	return wrapper
