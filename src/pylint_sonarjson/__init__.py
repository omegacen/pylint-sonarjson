"""SonarQube JSON reporter

Allows for configurable issue type, severity, and effort minutes per PyLint message.
The output format is JSON as described in
https://docs.sonarqube.org/latest/analysis/generic-issue/
"""

try:
    from pylint.lint.pylinter import PyLinter
except ImportError:
    from pylint.lint import PyLinter
from pylint_plugin_utils import get_checker

from .sonarjson_reporter import SonarJSONReporter
from .sonaroptions_checker import SonarOptionsChecker


def register(linter: PyLinter):
    linter.register_reporter(SonarJSONReporter)
    linter.register_checker(SonarOptionsChecker(linter))


def load_configuration(linter: PyLinter):
    sonar_checker = get_checker(linter, SonarOptionsChecker)
    sonar_checker.load_configuration()
