import sys
import os
from ConfigParser import ConfigParser
from os.path import exists as pathexists
from os.path import splitext
from subprocess import Popen

class Exists(Exception):
    """File exists"""
    pass

class ConfigMissing(Exception):
    """File exists"""
    pass


def make_venv(repo):
    """Make a virtualenv for the specified repo"""
    # TODO read a user or site wide config file for whether to use virtualenvwrapper
    # could have a "make virtualenv config with a possible 'internal' value"
    p = Popen(["virtualenv", "%s/.venv" % repo])
    p.wait()

def venv(repo):
    """Check the repo has a venv"""

    if pathexists("%s/.venv" % repo):
        # TODO: In this case we should test the version of these things
        return

    # Make the venv
    make_venv(repo)
    cfgfile = "%s/.veh.conf" % repo
    if not pathexists(cfgfile):
        raise ConfigMissing(cfgfile)

    cfg = ConfigParser()
    cfg.read(cfgfile)

    # Install each package in the venv
    packages = cfg.items("packages")
    for package in packages:
        pip = Popen([
                "bash",
                "-c",
                "source %s/.venv/bin/activate ; pip install -U %s" % (
                    repo,
                    package[1]
                    )
                ])
        pip.wait()

def edit_file(filename):
    """Open the filename in the editor.

    Actually does the whole pattern of opening a temp file.
    """
    _, extension = splitext(filename)
    from tempfile import mkstemp
    try:
        fd, tempfilename = mkstemp(suffix=".conf", text=True)
        print os.write(fd, CFG_TEMPLATE + "\n")
        os.close(fd)
    except Exception, e:
        print >>sys.stderr, "problem making temp file: " + str(e)
    else:
        editor = os.environ.get("VISUAL", os.environ.get("EDITOR", "edit"))
        try:
            p = Popen([editor, tempfilename])
            p.wait()
        except Exception, e:
            print >>sys.stderr, "problem running editor"
        else:
            # Copy the temp file in
            if pathexists(filename):
                os.remove(filename)
            os.rename(tempfilename, filename)

CFG_TEMPLATE="""[packages]
# enter package names here like
#   package = packagename
# the package names are passed directly to pip.
# This makes it easy to use either a pypi name:
#   package = packagename
# or a url:
#   package = http://pypi.python.org/packages/source/v/virtualenv/virtualenv-1.4.9.tar.gz#md5=c49067cab242b5ff8c7b681a5a99533a
# or a vc reference:
#   package = hg+http://domain/repo


# End
"""

def install(repo):
    """Install a veh config file

    Opens VISUAL (and EDITOR if it can't find that) with a template.
    """
    # TODO I think this should commit really. For now, it doesn't.
    # TODO we need to add the line to hgignore for the state file
    cfgfile = "%s/.veh.conf" % repo
    if pathexists(cfgfile):
        raise Exists(cfgfile)
    edit_file(cfgfile)

def edit(repo):
    """Edit the veh config file

    Opens VISUAL on the veh config file."""
    cfgfile = "%s/.veh.conf" % repo
    if pathexists(cfgfile):
        edit_file(cfgfile)


from cmd import Cmd

class VehCmd(Cmd):
    repo = None
    def do_install(self, *arg):
        """Install a virtualenv for the repository.
Actually installs just the config file. The venv is made on first use.
"""
        install(self.repo)

    def do_edit(self, *arg):
        """Edit the repositorys veh config file.
Opens VISUAL or EDITOR or /usr/bin/edit on your repositorys config file.
"""
        edit(self.repo)

    def do_cd(self, *arg):
        """Change directory into the repository.
First checks that the virtualenv for the repository has been built and builds
if necessary.
Changes directory and execs the user's SHELL.
"""
        venv(self.repo)
        os.chdir(self.repo)
        os.execl(os.environ["SHELL"])

    def do_noop(self, *arg):
        """No-op. Just checks the virtualenv.
"""
        venv(self.repo)
        

def main():
    from StringIO import StringIO
    cmdproc = VehCmd(StringIO())

    from optparse import OptionParser
    p = OptionParser()
    o,a = p.parse_args(sys.argv[1:])

    arg = a.pop(0)

    if arg == "help":
        cmdproc.onecmd("help%s" % ((" %s" % "".join(a)) if a else ""))
    else:
        # We ought to check the repo argument here
        repo = arg
        cmdproc.repo = repo

        # Now run the command
        command = a.pop(0)
        cmdproc.onecmd(command)


if __name__== "__main__":
    main()

# End