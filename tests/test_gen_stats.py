import importlib.util
import io
import os
from pathlib import Path
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

os.environ.setdefault('GH_TOKEN', 'test-token')
spec = importlib.util.spec_from_file_location('stats', Path(__file__).parents[1] / 'scripts/gen_stats.py')
stats = importlib.util.module_from_spec(spec)
spec.loader.exec_module(stats)


class GraphQLRetryTests(unittest.TestCase):
    def test_transient_errors_recover(self):
        for error in (HTTPError(stats.API, 502, 'Bad Gateway', {}, None),
                      HTTPError(stats.API, 429, 'Too Many Requests', {}, None),
                      TimeoutError()):
            with self.subTest(error=error), patch.object(stats.urllib.request, 'urlopen', side_effect=[error, io.BytesIO(b'{"data": {"ok": true}}')]) as request, patch.object(stats.time, 'sleep'):
                self.assertEqual(stats.graphql('query {}'), {'ok': True})
                self.assertEqual(request.call_count, 2)

    def test_authentication_error_is_not_retried(self):
        with patch.object(stats.urllib.request, 'urlopen', side_effect=HTTPError(stats.API, 401, 'Unauthorized', {}, None)) as request, patch.object(stats.time, 'sleep'):
            with self.assertRaises(HTTPError):
                stats.graphql('query {}')
            self.assertEqual(request.call_count, 1)

    def test_persistent_outage_stops_after_six_attempts(self):
        with patch.object(stats.urllib.request, 'urlopen', side_effect=HTTPError(stats.API, 502, 'Bad Gateway', {}, None)) as request, patch.object(stats.time, 'sleep'):
            with self.assertRaises(HTTPError):
                stats.graphql('query {}')
            self.assertEqual(request.call_count, 6)


if __name__ == '__main__':
    unittest.main()
