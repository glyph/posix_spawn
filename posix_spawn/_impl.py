import os

from ._lib import lib, ffi


class FileActions(object):
    def __init__(self):
        self._actions_t = ffi.gc(
            ffi.new("posix_spawn_file_actions_t *"),
            lib.posix_spawn_file_actions_destroy
        )

        lib.posix_spawn_file_actions_init(self._actions_t)

    def add_open(self, fd, path, oflag, mode):
        return lib.posix_spawn_file_actions_addopen(
            self._actions_t,
            fd,
            path,
            oflag,
            mode
        )

    def add_close(self, fd):
        return lib.posix_spawn_file_actions_addclose(self._actions_t, fd)

    def add_dup2(self, fd, new_fd):
        return lib.posix_spawn_file_actions_adddup2(self._actions_t, fd, new_fd)


def posix_spawn(path, args, env=None, file_actions=None, attributes=None):
    pid = ffi.new("pid_t *")

    if env is None:
        env = os.environ

    if file_actions is None:
        file_actions = ffi.NULL
    else:
        file_actions = file_actions._actions_t

    res = lib.posix_spawn(
        pid,
        path,
        file_actions,
        ffi.NULL,
        [ffi.new("char[]", arg) for arg in args],
        [ffi.new("char[]", b'{0}={1}'.format(key, value))
         for key, value in env.items()]
    )

    if res != 0:
        raise OSError(res, os.strerror(res), path)

    return pid[0]
