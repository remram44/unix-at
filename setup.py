import io
import os
from setuptools import setup


# pip workaround
os.chdir(os.path.abspath(os.path.dirname(__file__)))


# Need to specify encoding for PY3, which has the worst unicode handling ever
with io.open('README.rst', encoding='utf-8') as fp:
    description = fp.read()
setup(name='unix-at',
      version='1.1.1',
      py_modules=['unix_at'],
      install_requires=['python-dateutil'],
      description="Talk to the at(1) daemon, to schedule jobs for later",
      author="Remi Rampin",
      author_email='remirampin@gmail.com',
      maintainer="Remi Rampin",
      maintainer_email='remirampin@gmail.com',
      url='https://gitlab.com/remram44/unix-at',
      project_urls={
          'Homepage': 'https://gitlab.com/remram44/unix-at',
          'Documentation': 'https://unix-at.readthedocs.io/',
          'Say Thanks': 'https://saythanks.io/to/remram44',
          'Source': 'https://gitlab.com/remram44/unix-at',
          'Tracker': 'https://gitlab.com/remram44/unix-at/issues',
      },
      long_description=description,
      license='BSD-3-Clause',
      keywords=['unix', 'at', 'atq', 'job', 'jobs', 'schedule', 'scheduling',
                'later', 'delay', 'defer', 'deferred', 'queue', 'task'],
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Operating System :: POSIX',
          'Operating System :: Unix',
          'Programming Language :: Python',
          'Programming Language :: Unix Shell',
          'Topic :: Home Automation',
          'Topic :: System',
          'Topic :: Utilities'])
