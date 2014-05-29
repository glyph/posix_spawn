import os
import sys
import stat
import tempfile

from unittest import TestCase

from posix_spawn import posix_spawn, FileActions


scripts_dir = os.path.join(
    os.path.dirname(__file__),
    'scripts'
)

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

    if platform.system() == "Linux":
        test_raises_on_error.skip = "I can't even."

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


class FileActionsTests(TestCase):
    def test_empty_actions(self):
        fa = FileActions()
        pid = posix_spawn(
            sys.executable,
            [b'python', '-c', 'pass'],
            file_actions=fa
        )
        pid_info = os.waitpid(pid, 0)
        self.assertEqual(0, pid_info[1])

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
            self.assertEqual(0, fa.add_close(0))

            pid = posix_spawn(sys.executable, [
                b'python',
                os.path.join(scripts_dir, 'check_close.py'),
                closefile.name
            ],
            file_actions=fa)

            pid_info = os.waitpid(pid, 0)
            self.assertEqual(pid_info[1], 0)
            self.assertIn(b"is closed", closefile.read())

    def test_dup2(self):
        with tempfile.NamedTemporaryFile(mode=b'w+b') as dupfile:
            fa = FileActions()
            self.assertEqual(0, fa.add_dup2(dupfile.fileno(), 1))

            pid = posix_spawn(sys.executable, [
                b'python', '-c', 'import sys; sys.stdout.write("hello")'
            ], file_actions=fa)

            pid_info = os.waitpid(pid, 0)
            self.assertEqual(pid_info[1], 0)

            with open(dupfile.name, b'r+b') as stdout:
                self.assertIn("hello", stdout.read())
