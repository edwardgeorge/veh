import os
import subprocess
import shutil
import sys

import clonevirtualenv as clone
import virtualenv

from veh2 import venvdirops
from veh2 import venvrcops


class VehRepo(object):
    def __init__(self, repo):
        self.repo = repo
        self.root = repo.root

    def build_new_venv(self, rev=None, sitepackages=False, delete_old=False):
        def do_build(self, d, active):
            virtualenv.create_environment(d, sitepackages=sitepackages)
            venvrcops.install_rc_file(self, d)
        venvdirops.newvenv_operation_wrapper(self, do_build,
            delete_old=delete_old)

    def clone_new_venv(self, delete_old=False):
        def do_clone(self, newvenv, active):
            clone.clone_virtualenv(active, newvenv)
            venvrcops.install_rc_file(self, newvenv)
        venvdirops.newvenv_operation_wrapper(self, do_build,
            delete_old=delete_old)

    def refresh_venv(self, rev=None):
        raise NotImplementedError()

    def exec_python(self, command):
        raise NotImplementedError()

    def shell(self, command=None):
        raise NotImplementedError()

    def exec(self, command):
        raise NotImplementedError()

    def install(self):
        raise NotImplementedError()

    def active(self):
        raise NotImplementedError()

    def cleanup_inactive_virtualenvs(self):
        raise NotImplementedError()
