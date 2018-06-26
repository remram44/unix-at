import base64
import datetime
import pickle
import subprocess
import sys


class AtError(RuntimeError):
    """An error running the at(1) command.
    """


class Job(object):
    """Represents a job, parsed from the output of at(1).
    """
    def __init__(self, name, time):
        self.name = name
        assert isinstance(time, datetime.datetime)
        self.time = time


def list_jobs(at='at'):
    """Lists all the jobs currently in the queue.
    """
    # TODO: parse output
    return [Job(), Job()]


def get_script_for_job(job_name, at='at'):
    """Gets the full shell script associated with a job.

    :return: The script as bytes, or None if the job does not exist.
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

    :return: True on success, False if some jobs were not found.
    """
    if isinstance(job_name, (str, job)):
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
    """Submits a shell command to be run later with at(1).

    :return: The `Job` object for the new job.
    """
    if isinstance(command, collections.Iterable):
        command = ' '.join(shell_escape(c for c in command))
    # TODO: convert time
    proc = subprocess.Popen([at, time],
                            stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    _, stderr = proc.communicate(command)
    if proc.wait() != 0:
        raise AtError("process %s returned %d" % (at, proc.returncode))
    # TODO: parse output
    return Job()


def submit_python_job(func, time, *args, at='at', python=None, **kwargs):
    """Submits a Python function to be run later with at(1).

    The current interpreter will be used, unless `python` is set to a different
    executable.

    :param func: Either a fully-qualified function name (e.g.
    ``os.path.dirname``) or a function object (that will be pickled).
    :param time: A time specification in a format accepted by at(1) (e.g.
    ``2am + 2 days``) or a `datetime.datetime` object.

    :return: The `Job` object for the new job.
    """
    if isinstance(func, str):
        invoke = '_invoke(name=%r)' % func
    else:
        invoke = '_invoke(pkl=%r)' % pickle.dumps(func)
    return submit_shell_job([
        sys.executable,
        '-c',
        'from unix_at import _invoke; %s' % invoke,
        base64.b64encode(pickle.dumps((args, kwargs))),
    ])


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
