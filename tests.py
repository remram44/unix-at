import datetime
import unittest
import unix_at


class TestUnixAt(unittest.TestCase):
    def test_parse(self):
        job = unix_at.Job.parse(b'19\tTue Jun 26 11:32:00 2018 a remram')
        self.assertEqual(job.name, '19')
        self.assertEqual(job.time, datetime.datetime(2018, 6, 26, 11, 32, 0))

        job = unix_at.Job.parse(b'job 20 at Tue Jun 26 11:37:00 2018\n')
        self.assertEqual(job.name, '20')
        self.assertEqual(job.time, datetime.datetime(2018, 6, 26, 11, 37, 0))

    def test_convert(self):
        self.assertEqual(
            unix_at.convert_time(datetime.datetime(2018, 6, 26, 11, 48, 0)),
            '11:48 2018-06-26',
        )


if __name__ == '__main__':
    unittest.main()
