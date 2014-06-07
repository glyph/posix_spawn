import os
import sys
import stat
import textwrap

import pytest


from posix_spawn import posix_spawn, FileActions

executable = sys.executable.encode('ascii')
environ = getattr(os, 'environb', os.environ)

def exits(pid):
    (_pid, exit, _rusage) = os.wait4(pid, 0)
    return os.WEXITSTATUS(exit)


class TestPosixSpawn(object):
    def test_returns_pid(self, tmpdir):
        pidfile = tmpdir.join('pidfile')
        pid = posix_spawn(executable, [
            executable,
            b'-c',
            textwrap.dedent("""
                import os
                with open("{0!s}", "w") as pidfile:
                    pidfile.write(str(os.getpid()))
            """).format(pidfile).encode('ascii')
        ])

        assert exits(pid) == 0
        assert pid == int(pidfile.read())

    @pytest.mark.skipif(sys.platform.startswith("linux"),
                        reason="Is this even...")
    def test_raises_on_error(self):
        with pytest.raises(OSError) as error:
            posix_spawn(b'no_such_executable', [b'no_such_executable'])

        assert error.value.errno == 2
        assert error.value.strerror == 'No such file or directory'
        assert error.value.filename == b'no_such_executable'

    def test_specify_environment(self, tmpdir):
        envfile = tmpdir.join("envfile")
        pid = posix_spawn(executable, [
            executable,
            b'-c',
            textwrap.dedent("""
                import os
                with open("{0!s}", "w") as envfile:
                    envfile.write(os.environ['foo'])
            """).format(envfile).encode('ascii')],
            {b"foo": b"bar"}
        )

        assert exits(pid) == 0
        assert "bar" == envfile.read()

    def test_environment_is_none_inherits_environment(self, tmpdir):
        envfile = tmpdir.join("envfile")
        environ[b'inherits'] = b'environment'

        pid = posix_spawn(executable, [
            executable,
            b'-c',
            textwrap.dedent("""
                import os
                with open("{0!s}", "w") as envfile:
                    envfile.write(os.environ['inherits'])
            """).format(envfile).encode('ascii')],
            env=None
        )

        assert exits(pid) == 0
        assert "environment" == envfile.read()


class TestFileActions(object):
    def test_empty_actions(self):
        fa = FileActions()
        pid = posix_spawn(
            executable,
            [executable, b'-c', b'pass'],
            file_actions=fa
        )
        assert exits(pid) == 0

    def test_open_file(self, tmpdir):
        outfile = tmpdir.join('outfile')
        fa = FileActions()
        fa.add_open(
            1,
            str(outfile).encode('ascii'),
            os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
            stat.S_IRUSR | stat.S_IWUSR
        )

        pid = posix_spawn(executable, [
            executable,
            b'-c',
            textwrap.dedent("""
                import sys
                sys.stdout.write("hello")
            """).encode('ascii')],
            file_actions=fa
        )

        assert exits(pid) == 0
        assert "hello" == outfile.read()

    def test_close_file(self, tmpdir):
        closefile = tmpdir.join("closefile")
        fa = FileActions()
        fa.add_close(0)

        pid = posix_spawn(executable, [
            executable,
            b'-c',
            textwrap.dedent("""
                import os
                import sys
                import errno

                try:
                    os.fstat(0)
                except OSError as e:
                    if e.errno == errno.EBADF:
                        with open(sys.argv[1], 'w') as closefile:
                            closefile.write('is closed')
            """).encode('ascii'),
            str(closefile).encode('ascii')],
            file_actions=fa
        )

        assert exits(pid) == 0
        assert "is closed" == closefile.read()

    def test_dup2(self, tmpdir):
        dupfile = tmpdir.join("dupfile")
        with dupfile.open("w") as childfile:
            fa = FileActions()
            fa.add_dup2(childfile.fileno(), 1)

            pid = posix_spawn(executable, [
                executable,
                b'-c',
                textwrap.dedent("""
                    import sys
                    sys.stdout.write("hello")
                """).encode('ascii')],
                file_actions=fa
            )

            assert exits(pid) == 0

        assert "hello" == dupfile.read()
