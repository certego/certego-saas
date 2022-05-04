import contextlib
import logging
import unittest


class NoLogsTestCase(unittest.TestCase):
    def __init__(self, *args, max_logging_level=logging.WARNING, **kwargs):
        self._log = logging.getLogger(__name__)
        self.test_method = None
        self.max_logging_level = max_logging_level
        super().__init__(*args, **kwargs)

    @contextlib.contextmanager
    def assertNoLogs(self, logger=None, level=None):  # pylint: disable=invalid-name
        try:
            with self.assertLogs(logger=logger, level=level) as new_log:
                yield
        except AssertionError:
            pass
        else:
            for record in new_log.records:
                if record.levelno >= level:
                    raise AssertionError(
                        f"Unexpected logging message: '{record.message}' with level {record.levelname}"
                    )

    def no_logs(self):
        with self.assertNoLogs(level=self.max_logging_level):
            self.test_method()

    def run(self, result=None):
        self.test_method = getattr(self, self._testMethodName)
        setattr(self, self._testMethodName, self.no_logs)
        return super().run(result)
