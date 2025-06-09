import pytest
from django.test.runner import DiscoverRunner

class PytestTestRunner(DiscoverRunner):
    def run_tests(self, test_labels, extra_tests=None, **kwargs):
        argv = []
        if test_labels:
            argv.extend(test_labels)
        return pytest.main(argv) 