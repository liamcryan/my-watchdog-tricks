import logging
import os
import re
import getpass
from shutil import copyfile

import rever
from watchdog.events import RegexMatchingEventHandler

logging.getLogger('fsevents').setLevel(logging.ERROR)


# in the watchdog files, the Trick inherit the PatternMathingEventHandler
# the regex one seems more useful to me (at least in my case)
class TrickRE(RegexMatchingEventHandler):
    """Your tricks should subclass this class."""

    @classmethod
    def generate_yaml(cls):
        context = dict(module_name=cls.__module__,
                       klass_name=cls.__name__)
        template_yaml = """- %(module_name)s.%(klass_name)s:
  args:
  - argument1
  - argument2
  kwargs:
    patterns:
    - "*.py"
    - "*.js"
    ignore_patterns:
    - "version.py"
    ignore_directories: false
"""
        return template_yaml % context


@rever.rever(exception=(PermissionError,))
def copyfile_wrapper(a, b):
    # I have noticed when copying/pasting files to watched folder
    # corporate networks may have some period of time to perform security checks maybe?
    # Anyway, the create file event is fired
    # and when shutil.copyfile runs we hit a permission error.
    # This didn't happen when time.sleep happened prior to copying the file
    # which makes me think something corporate is happening & causing the permission error.
    # rever is a retry decorator I created in my early Python days & use a lot in my projects.
    # It is telling this function to execute again using exponential backoff
    # if a PermissionError is thrown.
    # Total pause time is 30s before throwing an error

    return copyfile(a, b)


class SyncFilesTrick(TrickRE):
    def __init__(self, src_dir=None, dest_dir=None, user_regexes=None, regexes=None, ignore_regexes=None,
                 ignore_directories=False, create_dest_dir_if_not_exist=None):
        if not regexes:
            regexes = []
        user = getpass.getuser()
        if not user_regexes or user_regexes.get(user) is None or user_regexes.get(user) == [None]:
            user_regexes = {}
        regexes = user_regexes.get(user, []) + regexes
        if not regexes:
            ignore_regexes = ['.*']

        super().__init__(regexes=regexes, ignore_regexes=ignore_regexes, ignore_directories=ignore_directories)
        self.src_dir = src_dir
        self.dest_dir = dest_dir
        self.create_dest_dir_if_not_exist = create_dest_dir_if_not_exist

    def matches_regex(self, search_str):
        # watchdogs regex doesn't catch my regex in all cases???
        # but this does
        for regex in self.regexes:
            if re.search(regex, search_str):
                return True

    def move_file(self, src_path):
        if not self.matches_regex(src_path):
            return

        if self.create_dest_dir_if_not_exist:
            delta_dirs = os.path.dirname(src_path[len(self.src_dir) + 1:])
            os.makedirs(os.path.join(self.dest_dir, delta_dirs), exist_ok=True)

        copyfile_wrapper(src_path, os.path.join(self.dest_dir, src_path[len(self.src_dir) + 1:]))

    def delete_file(self, src_path):
        if not self.matches_regex(src_path):
            return

        try:
            os.remove(
                os.path.join(self.dest_dir, src_path[len(self.src_dir) + 1:])
            )
        except FileNotFoundError:
            pass

    def on_modified(self, event):
        self.move_file(event.src_path)

    def on_deleted(self, event):
        self.delete_file(event.src_path)

    def on_created(self, event):
        self.move_file(event.src_path)

    def on_moved(self, event):
        self.delete_file(event.src_path)
        self.move_file(event.dest_path)
