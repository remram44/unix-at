import datetime
import os
import time
import unittest
import unix_at


class TestUnit(unittest.TestCase):
    def test_parse(self):
        job = unix_at.Job.parse(b'19\tTue Jun 26 11:32:00 2018 a remram')
        self.assertEqual(job.name, '19')
        self.assertEqual(job.time, datetime.datetime(2018, 6, 26, 11, 32, 0))

        job = unix_at.Job.parse(b'job 20 at Tue Jun 26 11:37:00 2018\n')
        self.assertEqual(job.name, '20')
        self.assertEqual(job.time, datetime.datetime(2018, 6, 26, 11, 37, 0))

        job = unix_at.Job.parse(b'1\t2018-11-15 16:15 a root')
        self.assertEqual(job.name, '1')
        self.assertEqual(job.time, datetime.datetime(2018, 11, 15, 16, 15, 0))

    def test_convert(self):
        self.assertEqual(
            unix_at.convert_time(datetime.datetime(2018, 6, 26, 11, 48, 0)),
            '11:48 2018-06-26',
        )


class TestFunctional(unittest.TestCase):
    def test_real(self):
        """Test by talking to the actual at daemon."""
        self.assertEqual(unix_at.list_jobs(), [])
        if os.path.exists('/tmp/job1'):
            os.remove('/tmp/job1')
        if os.path.exists('/tmp/job2'):
            os.remove('/tmp/job2')
        job1 = unix_at.submit_shell_job('echo one >/tmp/job1',
                                       'now + 1 minutes')
        jobs = unix_at.list_jobs()
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs, [job1])
        job2 = unix_at.submit_python_job(open, 'now + 2 minutes',
                                         '/tmp/job2', 'w')
        jobs = unix_at.list_jobs()
        self.assertEqual(len(jobs), 2)
        self.assertEqual(set(jobs), set([job1, job2]))
        script = unix_at.get_script_for_job(job1.name)
        # Some systems will wrap execution in `SHELL << 'end'\n...\nend`
        expected = b'echo one >/tmp/job1'
        self.assertTrue(script.splitlines()[-1].strip() == expected or
                        script.splitlines()[-2].strip() == expected)
        time.sleep(60)
        self.assertEqual(unix_at.list_jobs(), [job2])
        self.assertTrue(os.path.exists('/tmp/job1'))
        self.assertFalse(os.path.exists('/tmp/job2'))
        time.sleep(60)
        self.assertEqual(unix_at.list_jobs(), [])
        self.assertTrue(os.path.exists('/tmp/job2'))


if __name__ == '__main__':
    unittest.main()
