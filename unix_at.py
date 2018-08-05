import base64
import collections
import datetime
import pickle
import re
import subprocess
import sys


__version__ = '0.2'


class AtError(RuntimeError):
    """An error running the `at(1)` command.
    """


class Job(object):
    """Represents a job, parsed from the output of `at(1)`.
    """
    def __init__(self, name, time):
        self.name = name
        """Name of the job, shown by ``at -l``"""
        assert isinstance(time, datetime.datetime)
        self.time = time
        """
        Time at which the job is to run, as a :py:class:`datetime.datetime`
        object.
        """

    _regexes = [
        re.compile(br'^([0-9]+)\t(.+) a [^ ]+(:?\n?)$'),
        re.compile(br'^job ([0-9]+) at (.+)(:?\n?)$'),
    ]

    @classmethod
    def parse(cls, line):
        from dateutil.parser import parse

        for regex in cls._regexes:
            match = regex.match(line)
            if match is not None:
                return Job(match.group(1).decode('ascii'),
                           parse(match.group(2)))


_safe_shell_chars = set(b"ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                        b"abcdefghijklmnopqrstuvwxyz"
                        b"0123456789"
                        b"-+=/:.,%_")


def shell_escape(s):
    r"""Given bl"a, returns "bl\\"a".
    """
    if not isinstance(s, bytes):
        s = s.encode('utf-8')
    if not s or any(c not in _safe_shell_chars for c in s):
        return b'"%s"' % (s.replace(b'\\', b'\\\\')
                           .replace(b'"', b'\\"')
                           .replace(b'`', b'\\`')
                           .replace(b'$', b'\\$'))
    else:
        return s


def convert_time(dt):
    """Converts a datetime object into a format `at(1)` will accept.
    """
    from dateutil import tz

    if dt.tzinfo is not None:
        dt = dt.astimezone(tz.tzlocal())
    return dt.strftime('%H:%M %Y-%m-%d')


def list_jobs(at='at'):
    """Lists all the jobs currently in the queue.

    :param at: Overrides the location of the `at` binary (defaults to
      ``'at'``).
    :return: A `list` of :class:`Job` objects.
    """
    out = subprocess.check_output([at, '-l'])
    return [Job.parse(line) for line in filter(None, out.split(b'\n'))]


def get_script_for_job(job_name, at='at'):
    """Gets the full shell script associated with a job.

    :param job_name: Either the name of the job as a string, like it is shown
      by ``at -l``, or a :class:`Job` object.
    :param at: Overrides the location of the `at` binary (defaults to
      ``'at'``).
    :return: The script as `bytes`, or `None` if the job does not exist.
    """
    if isinstance(job_name, Job):
        job_name = job_name.name
    try:
        return subprocess.check_output([at, '-c', job_name])
    except subprocess.CalledProcessError as e:
        if e.returncode == 1:
            return None
        else:
            raise AtError("process %s returned %d" % (at, e.returncode))


def cancel_job(job_name, at='at'):
    """Cancels one or multiple jobs from their names or `Job` objects.

    :param job_name: An iterable of either names of jobs as strings, like it is
      shown by ``at -l``, or :class:`Job` objects.
    :param at: Overrides the location of the `at` binary (defaults to
      ``'at'``).
    :return: `True` on success, `False` if some jobs were not found.
    """
    if isinstance(job_name, (str, Job)):
        return cancel_job([job_name], at='at')
    jobs = []
    for job_name in job_name:
        if isinstance(job_name, Job):
            jobs.append(job_name.name)
        else:
            jobs.append(job_name)
    proc = subprocess.Popen([at, '-r'] + jobs,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc.communicate()
    return proc.wait() == 0


def submit_shell_job(command, time, at='at'):
    """Submits a shell command to be run later with `at(1)`.

    :param command: A command as a single string or an iterable of words,
      similar to what is expected by the first argument to
      :py:class:`subprocess.Popen`.
    :param time: Either a :py:class:`datetime.datetime` object, or a string in
      the format accepted by `at(1)`, such as ``"now + 1 minute"`` or
      ``"2m + 2 days"``.
    :param at: Overrides the location of the `at` binary (defaults to
      ``'at'``).
    :return: The :class:`Job` object for the new job.

    Note that `at(1)` usually restores the working directory and environment
    variables when it runs the job.
    """
    if isinstance(command, bytes):
        pass
    elif isinstance(command, str):
        command = command.encode('utf-8')
    elif isinstance(command, collections.Iterable):
        command = b' '.join(shell_escape(c) for c in command)
    else:
        raise TypeError("command should be bytes (or str, or list of bytes or "
                        "str)")
    if isinstance(time, datetime.datetime):
        time = convert_time(time)
    proc = subprocess.Popen([at, time],
                            stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    _, stderr = proc.communicate(command)
    if proc.wait() != 0:
        raise AtError("process %s returned %d" % (at, proc.returncode))
    for line in stderr.split(b'\n'):
        if line.startswith(b'warning:'):
            continue
        return Job.parse(line)


def submit_python_job(func, time, *args, **kwargs):
    """Submits a Python function to be run later with `at(1)`.

    The current interpreter will be used, unless `python` is set to a different
    executable.

    :param func: Either a fully-qualified function name (e.g.
      ``os.path.dirname``) or a function object (that will be pickled).
    :param time: Either a :py:class:`datetime.datetime` object, or a string in
      the format accepted by `at(1)`, such as ``"now + 1 minute"`` or
      ``"2m + 2 days"``.
    :param at: Overrides the location of the `at` binary (defaults to
      ``'at'``).
    :return: The :class:`Job` object for the new job.
    """
    at = kwargs.pop('at', 'at')
    python = kwargs.pop('python', sys.executable)
    if isinstance(func, str):
        invoke = b'_invoke(name=%r)' % func
    else:
        invoke = b'_invoke(pkl=%r)' % pickle.dumps(func)
    return submit_shell_job(
        [
            python,
            b'-c',
            b'from unix_at import _invoke; %s' % invoke,
            base64.b64encode(pickle.dumps((args, kwargs))),
        ],
        time,
        at=at,
    )


def _invoke(**kwargs):
    """Internal function, used by `submit_python_job`.
    """
    if 'name' in kwargs:
        import importlib

        module, func = kwargs.pop('name').rsplit('.', 1)
        module = importlib.import_module(module)
        func = getattr(module, func)
    elif 'pkl' in kwargs:
        func = pickle.loads(kwargs.pop('pkl'))
    else:
        raise RuntimeError("_invoke() didn't receive a target in any "
                           "supported way")
    if kwargs:
        raise RuntimeError("_invoke() received multiple targets")

    args, kwargs = pickle.loads = pickle.loads(base64.b64decode(sys.argv[1]))
    func(*args, **kwargs)
