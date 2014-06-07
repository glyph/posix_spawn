import os

from ._lib import lib, ffi


def _handle_error(errno, path=None):
    if path is not None:
        raise OSError(errno, os.strerror(errno), path)
    else:
        raise OSError(errno, os.sterror(errno))


class FileActions(object):
    def __init__(self):
        self._actions_t = ffi.gc(
            ffi.new("posix_spawn_file_actions_t *"),
            lib.posix_spawn_file_actions_destroy
        )

        lib.posix_spawn_file_actions_init(self._actions_t)

    def add_open(self, fd, path, oflag, mode):
        if not isinstance(fd, int):
            raise TypeError(
                "fd must be an int not {0}.".format(type(fd).__name__))

        if not isinstance(path, bytes):
            raise TypeError(
                "path must be bytes not {0}.".format(type(path).__name__))

        if not isinstance(oflag, int):
            raise TypeError(
                "oflag must be an int not {0}.".format(type(oflag.__name__)))

        if not isinstance(mode, int):
            raise TypeError(
                "mode must be int not {0}.".format(type(mode).__name__))

        res = lib.posix_spawn_file_actions_addopen(
            self._actions_t,
            fd,
            path,
            oflag,
            mode
        )
        if res != 0:
            _handle_error(res)

    def add_close(self, fd):
        if not isinstance(fd, int):
            raise TypeError(
                "fd must be an int not {0}.".format(type(fd).__name__))

        return lib.posix_spawn_file_actions_addclose(self._actions_t, fd)

    def add_dup2(self, fd, new_fd):
        if not isinstance(fd, int):
            raise TypeError(
                "fd must be an int not {0}.".format(type(fd).__name__))

        if not isinstance(new_fd, int):
            raise TypeError(
                "new_fd must be an int not {0}.".format(type(new_fd).__name__))

        return lib.posix_spawn_file_actions_adddup2(
            self._actions_t, fd, new_fd)


def posix_spawn(path, args, env=None, file_actions=None, attributes=None):
    if not isinstance(path, bytes):
        raise TypeError(
            "path must be bytes not {0}.".format(type(path).__name__))

    pid = ffi.new("pid_t *")

    if env is None:
        env = getattr(os, 'environb', os.environ)

    if file_actions is None:
        file_actions = ffi.NULL
    else:
        if not isinstance(file_actions, FileActions):
            raise TypeError(
                "file_actions must be FileActions not {0}.".format(
                    type(file_actions).__name__))

        file_actions = file_actions._actions_t

    arg_list = [ffi.new("char[]", arg) for arg in args] + [ffi.NULL]

    env_list = [ffi.new("char[]", b"=".join([key, value]))
                for key, value in env.items()] + [ffi.NULL]

    res = lib.posix_spawn(
        pid,
        path,
        file_actions,
        ffi.NULL,
        arg_list,
        env_list
    )

    if res != 0:
        _handle_error(res)

    return pid[0]
