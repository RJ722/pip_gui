from __future__ import absolute_import

import sys
import threading

from pip.commands.search import highest_version
from pip import parseopts
from io import StringIO

import tkinter as tk
from tkinter import ttk

search_hits = {}

'''

class WidgetHandler(logging.Handler):
    """
    Log text to a Tkinter widget
    """

    def __init__(self, widget):
        logging.Handler.__init__(self)
        self.widget = widget

    def emit(self, content_text):
        msg = self.format(content_text)
        def update():
            self.widget.config(text=msg)
        self.widget.after(0, update)
'''

class MultiItemsList(object):

    def __init__(self, parent, headers_list=None):
        """
        Initialize variables needed for creating Treeview
        """

        self.scroll_tree = None
        self.parent = parent
        self.headers_list = headers_list
        self.items_list = None
        self.create_treeview()
        self.create_headers()

    def create_treeview(self):
        """
        Create a multi items list consisting of a frame, horizontal and vertical
        scroll bar and Treeview
        """

        self.myframe = ttk.Frame(self.parent)
        self.myframe.grid(row=1, column=0, columnspan=2, sticky='nswe')

        self.scroll_tree = ttk.Treeview(
            self.myframe,
            columns=self.headers_list,
            show='headings')

        '''
        FIX : Scrollbar is creating problems while changing frame
        vrtl_scrbar = ttk.Scrollbar(
            orient="vertical",
            command=self.scroll_tree.yview)
        hrtl_scrbar = ttk.Scrollbar(
            orient="horizontal",
            command=self.scroll_tree.xview)

        self.scroll_tree.configure(
            yscrollcommand=vrtl_scrbar.set,
            xscrollcommand=hrtl_scrbar.set)
        '''
        self.scroll_tree.grid(column=0, row=0, sticky='nswe', in_=self.myframe)
        '''
        vrtl_scrbar.grid(column=1, row=0, sticky='ns', in_=self.myframe)
        hrtl_scrbar.grid(column=0, row=1, sticky='ew', in_=self.myframe)
        '''
        self.myframe.grid_columnconfigure(0, weight=1)
        self.myframe.grid_rowconfigure(0, weight=1)

    def create_headers(self):

        for header in self.headers_list:
            self.scroll_tree.heading(header, text=header)
            self.scroll_tree.column(header, width=30)

    def populate_rows(self, items_list=None):

        self.scroll_tree.delete(*self.scroll_tree.get_children())
        self.items_list = items_list
        for item in self.items_list:
            self.scroll_tree.insert('', 'end', values=item)



class Redirect:
    """Context manager for temporarily redirecting stdout/err.
    Simplified and generalize from contextlib.redirect_stdout.
    """

    def __init__(self, stdfile, new_target):
        self._stdfile = stdfile  # 'stdout' or 'stderr'
        self._new_target = new_target

    def __enter__(self):
        self._old = getattr(sys, self._stdfile)
        setattr(sys, self._stdfile, self._new_target)
        return self._new_target

    def __exit__(self, exctype, excinst, exctb):
        setattr(sys, self._stdfile, self._old)


# For GUI version, redirects would be here, done once.
# Put in runpip for prototype testing in text mode, so can print.
def runpip(argstring):
    """Run pip with argument string containing command and options.

    :param argstring: is quoted version of what would follow 'pip'
      on command line.
    """
    sysout = StringIO()
    syserr = StringIO()

    import pip

    with Redirect('stdout', sysout) as f1, Redirect('stderr', syserr) as f2:
        #Clear all loggers
        pip.logger.consumers = []

        status = pip.main(argstring.split())
        out = sysout.getvalue()
        err = syserr.getvalue()
        #print('{}\n{}\n{}'.format(status, out, err))

    sysout.seek(0); sysout.truncate(0)
    syserr.seek(0); syserr.truncate(0)
    return status, out, err

def pip_search_command(package_name=None, thread_queue=None):
    """
    Uses pip.commands.search.SearchCommand to retrieve results of 'pip search'
    """

    from pip_tkinter.pip_extensions import GUISearchCommand

    search_object = GUISearchCommand()
    cmd_name, cmd_args = parseopts(['search', package_name])
    search_object.main(cmd_args)
    thread_queue.put(search_object.get_search_results())

def pip_list_command():
    """
    Lists all installed packages
    """

    from pip_tkinter.pip_extensions import GUIListCommand

    list_object = GUIListCommand()
    cmd_name, cmd_args = parseopts(['list','--no-cache-dir'])
    list_object.main(cmd_args)
    return list_object.get_installed_packages_list()

def pip_list_outdated_command():
    """
    Lists all outdated installed packages
    """

    from pip_tkinter.pip_extensions import GUIListCommand

    list_object = GUIListCommand()
    cmd_name, cmd_args = parseopts(['list','--outdated'])
    list_object.main(cmd_args)
    return list_object.get_installed_packages_list()

def pip_show_command(package_args):
    """
    Show details of a installed package
    """
    return runpip('show --no-cache-dir {}'.format(package_args))

def pip_install_from_PyPI(package_args, thread_queue):
    """
    Wrapper for installing pip package from PyPI
    """
    stat, out, err = runpip('install -U {}'.format(package_args))
    print (stat)
    print (out)
    print (err)
    thread_queue.put(out)

def pip_install_from_local_archive(package_args):
    """
    Wrapper for installing pip package from local Archive
    """
    return runpip('install {}'.format(package_args))

def pip_install_from_requirements(package_args):
    """
    Wrapper for installing pip package from requirements file
    """
    return runpip('install -r {}'.format(package_args))

def pip_install_from_alternate_repo(package_args):
    """
    Wrapper for installing pip package from Pythonlibs
    """
    return runpip('install --index-url{}'.format(package_args))

def pip_uninstall(package_args):
    """
    Uninstall packages
    """
    return runpip('uninstall --yes {}'.format(package_args))
