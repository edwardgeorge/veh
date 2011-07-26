import os
import tempfile

VENV_DIR = '.venvs'
ACTIVEFILE = '.active'
VENV_PREFIX = 'venv-'


def get_venv_dir(repo):
    "Return the path of the repo's virtualenv directory."
    return os.path.join(repo.root, VENV_DIR)


def get_active_symlink(repo):
    "Return the path to the repo's active virtualenv symlink."
    return os.path.join(get_venv_dir(repo), ACTIVEFILE)


def get_active_venv(repo):
    "Return the path of the currently active symlink."
    ln = get_active_symlink(repo)
    if os.path.exists(ln):
        return os.path.abspath(os.readlink(ln))


def get_all_venvs(repo):
    "Return a list of the paths all virtualenvs in the repo."
    d = get_venv_dir(repo)
    try:
        root, dirs, files = os.walk(d)
        return [os.path.join(root, i) for i in dirs
            if i.startswith(VENV_PREFIX)]
    except StopIteration, e:
        return []


def make_venv_active(repo, venv):
    "Make the given virtualenv the active one for the repo."
    venvdir = get_venv_dir(repo)
    activefile = get_active_symlink(repo)
    tmpfile = "%s.tmp" % activefile
    if os.path.exists(tmpfile):
        raise Exception('tmpfile %r exists.' % tmpfile)
    os.symlink(venv, tmpfile)
    os.rename(tmpfile, activefile)


def new_venv_dirname(repo):
    "Generate a new virtualenv directory name."
    return tempfile.mktemp(prefix=VENV_PREFIX, dir=get_venv_dir(repo))


def remove_inactive_venvs(repo):
    "Remove all inactive virtualenvs."
    active = get_active_venv(repo)
    for d in get_all_venvs(repo):
        if d != active:
            remove_venv(repo, d)


def remove_venv(repo, venv, check_active=False):
    """Remove the given virtualenv from the filesystem.

    If check_active is True (default) then the active symlink
    is removed if the given virtualenv was currently active.

    """
    shutil.rmtree(venv)
    if check_active and venv == get_active_venv(repo):
        os.unlink(get_active_symlink(repo))


def newvenv_operation_wrapper(repo, op,
       make_active=True, delete_old=False, **kw):
    """Wrapper function for performing operations with new virtualenvs.

    Calls op with the repo, the path to the new virtualenv, the path
    of the existing active virtualenv, and any other keyword arguments
    passed to the wrapper.

    After op() finishes the wrapper will make the new virtualenv active
    if make_active is true and will delete the old virtualenv if
    delete_old is true.

    """
    active = venvdirops.get_active_venv(repo)
    d = new_venv_dirname(repo)
    try:
        op(repo, d, **kw)
    except Exception, e:
        if os.path.exists(d):
            shutil.rmtree(d)
        raise
    if make_active:
        make_venv_active(repo, d, active)
        if delete_old and active:
            remove_venv(repo, active)
    return d
