unix-at
=======

This tiny library allows you to talk to the `at(1)` system, available on most UNIX machines, to schedule jobs to be run later.

Using `at(1)` can be much more light-weight than running a full-fledged job-processing system such as `Celery <http://www.celeryproject.org/>`__ if you are running very few jobs, however the performance will be much lower if you are running a considerable amount of tasks.

Example
-------

..  code-block:: python

    import unix_at

    job = unix_at.submit_shell_job(['touch', '/some/file'])
    unix_at.cancel_job(job)
    job = unix_at.submit_python_job(os.mkdir, 'now + 1 hour', '/some/dir')
