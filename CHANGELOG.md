Changelog
=========

1.2 (2023-10-11)
----------------

Bugfixes:
* Avoid collision with new `match` keyword
* Read queue name if present in `at -l` output, only get queue "a"

Other:
* Switch project host from GitLab to GitHub

1.1.2 (2023-01-12)
------------------

Bugfixes:
* Support Python 3.10, where collections.Iterable is no longer available

1.1.1 (2021-01-07)
------------------

Bugfixes:
* Raise exceptions on problems, avoid returning None

1.1 (2018-11-14)
----------------

Enhancements:
* Add comparison operators to Job

Bugfixes:
* Call `atrm` rather than `at -r`, which seems more compatible

1.0 (2018-08-05)
----------------

Enhancements:
* Have `submit_python_job()` accept `python=None`
* Include stderr in AtError
* Add `__repr__` to Job

Bugfixes:
* Fix `at` argument not passing through `cancel_job()`

0.2 (2018-06-26)
----------------

Bugfixes:
* Fixes bytes issues on Python 3
* Fixes calling `submit_shell_job()` with a single command instead of iterable

0.1 (2018-06-26)
----------------

Initial release
