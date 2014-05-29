import os
import sys
import stat
import tempfile

from unittest import TestCase

from posix_spawn import posix_spawn, FileActions


class PosixSpawnTests(TestCase):
    def test_returns_pid(self):
        with tempfile.NamedTemporaryFile(mode=b'r+b') as pidfile:
            pid = posix_spawn(sys.executable, [
                b'python',
                b'-c',
                (b'import os; '
                 b'open({0!r}, "w").write(str(os.getpid()))'.format(
                    pidfile.name))
            ])

            pid_info = os.waitpid(pid, 0)

            self.assertEqual(pid, pid_info[0])
            self.assertEqual(pid_info[1], 0)
            self.assertEqual(pid, int(pidfile.read()))

    def test_raises_on_error(self):
        with self.assertRaises(OSError) as error:
            posix_spawn(b'no_such_executable', [b'no_such_executable'])

        self.assertEqual(error.exception.errno, 2)
        self.assertEqual(error.exception.strerror, 'No such file or directory')
        self.assertEqual(error.exception.filename, b'no_such_executable')

    def test_specify_environment(self):
        with tempfile.NamedTemporaryFile(mode=b'r+b') as envfile:
            pid = posix_spawn(sys.executable, [
                b'python',
                b'-c',
                (b'import os; '
                 b'open({0!r}, "w").write(str(os.environ))'.format(
                    envfile.name))
            ],
            {b'foo': b'bar'})

            os.waitpid(pid, 0)
            self.assertIn(b"'foo': 'bar'", envfile.read())

    def test_environment_is_none_inherits_environment(self):
        with tempfile.NamedTemporaryFile(mode=b'r+b') as envfile:
            os.environ[b'inherits'] = 'environment'

            pid = posix_spawn(sys.executable, [
                b'python',
                b'-c',
                (b'import os; '
                 b'open({0!r}, "w").write(str(os.environ))'.format(
                    envfile.name))
            ],
            env=None)

            os.waitpid(pid, 0)

            self.assertIn(b"'inherits': 'environment'", envfile.read())

    def test_open_file(self):
        with tempfile.NamedTemporaryFile(mode=b'r+b') as outfile:
            fa = FileActions()
            self.assertEqual(0, fa.add_open(
                1,
                outfile.name,
                os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
                stat.S_IRUSR | stat.S_IWUSR
            ))

            pid = posix_spawn(sys.executable, [
                b'python',
                b'-c',
                b'print ("hello")',
            ],
            file_actions=fa)

            os.waitpid(pid, 0)
            self.assertIn(b"hello", outfile.read())

    def test_close_file(self):
        with tempfile.NamedTemporaryFile(mode=b'r+b') as closefile:
            fa = FileActions()
            self.assertEqual(0, fa.add_close(1))

            pid = posix_spawn(sys.executable, [
                b'python',
                b'-c',
                (b'import sys; '
                 b'open({0!r}, "w").write(str(sys.stdout.closed))'.format(
                    closefile.name))
            ],
            file_actions=fa)

            os.waitpid(pid, 0)
            self.assertIn(b"True", closefile.read())
