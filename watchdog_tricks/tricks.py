import os
import re
from shutil import copyfile

from watchdog.events import RegexMatchingEventHandler

import logging

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


class SyncTrick(TrickRE):
    def __init__(self, src_dir=None, dest_dir=None, user_regexes=None, regexes=None, ignore_directories=False):
        # function to get user
        user = os.path.basename(os.getenv('HOME'))
        if not regexes:
            regexes = []
        regexes = user_regexes.get(user, []) + regexes
        if not regexes:
            raise Exception('Must specify regexes or user_regexes')
        super().__init__(regexes=regexes, ignore_directories=ignore_directories)
        self.src_dir = src_dir
        self.dest_dir = dest_dir

    def matches_regex(self, search_str):
        # watchdogs regex doesn't catch my regex in all cases???
        # but this does
        for regex in self.regexes:
            if re.search(regex, search_str):
                return True

    def move_file(self, src_path):
        if not self.matches_regex(src_path):
            return

        copyfile(
            src_path,
            os.path.join(self.dest_dir, src_path[len(self.src_dir) + 1:])
        )

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
