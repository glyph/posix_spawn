import os
import sys
import stat
import textwrap

import pytest


from posix_spawn import posix_spawn, FileActions

class TestPosixSpawn(object):
    def test_returns_pid(self, tmpdir):
        pidfile = tmpdir.join('pidfile')
        pid = posix_spawn(sys.executable, [
            b'python',
            b'-c',
            textwrap.dedent("""
                import os
                with open("{0!s}", "w") as pidfile:
                    pidfile.write(str(os.getpid()))
            """).format(pidfile)
        ])

        pid_info = os.waitpid(pid, 0)

        assert pid == pid_info[0]
        assert pid_info[1] == 0
        assert pid == int(pidfile.read())

    def test_raises_on_error(self):
        with pytest.raises(OSError) as error:
            posix_spawn(b'no_such_executable', [b'no_such_executable'])

        assert error.value.errno == 2
        assert error.value.strerror == 'No such file or directory'
        assert error.value.filename == b'no_such_executable'

    def test_specify_environment(self, tmpdir):
        envfile = tmpdir.join("envfile")
        pid = posix_spawn(sys.executable, [
            b'python',
            b'-c',
            textwrap.dedent("""
                import os
                with open("{0!s}", "w") as envfile:
                    envfile.write(os.environ['foo'])
            """).format(envfile)],
            {b"foo": b"bar"}
        )

        os.waitpid(pid, 0)
        assert b"bar" == envfile.read()

    def test_environment_is_none_inherits_environment(self, tmpdir):
        envfile = tmpdir.join("envfile")
        os.environ[b'inherits'] = 'environment'

        pid = posix_spawn(sys.executable, [
            b'python',
            b'-c',
            textwrap.dedent("""
                import os
                with open("{0!s}", "w") as envfile:
                    envfile.write(os.environ['inherits'])
            """).format(envfile)],
            env=None
        )

        os.waitpid(pid, 0)

        assert b"environment" == envfile.read()


class TestFileActions(object):
    def test_empty_actions(self):
        fa = FileActions()
        pid = posix_spawn(
            sys.executable,
            [b'python', '-c', 'pass'],
            file_actions=fa
        )
        pid_info = os.waitpid(pid, 0)
        assert 0 == pid_info[1]

    def test_open_file(self, tmpdir):
        outfile = tmpdir.join('envfile')
        fa = FileActions()
        assert 0 == fa.add_open(
            1,
            str(outfile),
            os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
            stat.S_IRUSR | stat.S_IWUSR
        )

        pid = posix_spawn(sys.executable, [
            b'python',
            b'-c',
            textwrap.dedent("""
                import sys
                sys.stdout.write("hello")
            """)],
            file_actions=fa
        )

        os.waitpid(pid, 0)
        assert b"hello" == outfile.read()

    def test_close_file(self, tmpdir):
        closefile = tmpdir.join("closefile")
        fa = FileActions()
        assert 0 == fa.add_close(0)

        pid = posix_spawn(sys.executable, [
            b'python',
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
            """),
            str(closefile)],
            file_actions=fa
        )

        pid_info = os.waitpid(pid, 0)
        assert pid_info[1] == 0
        assert b"is closed" == closefile.read()

    def test_dup2(self, tmpdir):
        dupfile = tmpdir.join("dupfile")
        with dupfile.open("w") as childfile:
            fa = FileActions()
            assert 0 == fa.add_dup2(childfile.fileno(), 1)

            pid = posix_spawn(sys.executable, [
                b'python', '-c',
                textwrap.dedent("""
                    import sys
                    sys.stdout.write("hello")
                """)],
                file_actions=fa
            )

            pid_info = os.waitpid(pid, 0)
            assert pid_info[1] == 0

        assert "hello" == dupfile.read()
