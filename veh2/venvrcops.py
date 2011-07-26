from __future__ import with_statement
import os


def install_rc_file(self, venv):
    rcfile = os.path.join(venv, '.startup_rc')
    is_osx = sys.platform == 'darwin'
    bashrc, bash_profile = map(os.path.expanduser,
        ['~/.bashrc', '~/.bash_profile'])
    with open(rcfile, "w") as out:
        if not is_osx and os.path.exists(bashrc):
            out.write("source %s\n" % bashrc)
        elif is_osx and os.path.exists(bash_profile):
            out.write("source %s\n" % bash_profile)
        out.write("source %s\n" % os.path.join(venv, 'bin', 'activate'))
