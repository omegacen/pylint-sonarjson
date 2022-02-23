"""SonarQube JSON reporter

Allows for configurable issue type, severity, and effort minutes per PyLint message.
The output format is JSON as described in
https://docs.sonarqube.org/latest/analysis/generic-issue/
"""

import json
from typing import Optional

from pylint.checkers import BaseChecker
from pylint.exceptions import InvalidArgsError
from pylint.interfaces import IReporter, IAstroidChecker
from pylint.lint.pylinter import PyLinter
from pylint.message import Message
from pylint.reporters.base_reporter import BaseReporter
from pylint.reporters.ureports.nodes import Section

DEFAULT_SEVERITY = "MINOR"
DEFAULT_EFFORT = 5
DEFAULT_TYPE = "CODE_SMELL"
ALLOWED_SEVERITIES = (
    "BLOCKER",
    "CRITICAL",
    "MAJOR",
    "MINOR",
    "INFO"
)
ALLOWED_TYPES = (
    "BUG",
    "VULNERABILITY",
    "CODE_SMELL"
)


class DummySonarRulesChecker(BaseChecker):
    """Dummy checker that only registers options."""

    __implements__ = IAstroidChecker

    name = "SonarQube JSON output"
    level = 0
    options = (
        (
            "sonar-rules",
            {
                "default": "",
                "type": "csv",
                "metavar": "<rules>",
                "help": "Comma-separated list of rules, their severity, and the"
                        " minutes of efforts to fix the issues. The syntax is"
                        " <message id>:<severity>[:<effort minutes>[:<type>]]."
                        " So e.g. --sonar-rules=C0326:MINOR:1,E0102:MAJOR:5:BUG"
            },
        ),
        (
            "sonar-default-severity",
            {
                "default": DEFAULT_SEVERITY,
                "type": "string",
                "metavar": "<severity>",
                "help": "Issue severity for rules not specified in --sonar-rules."
            },
        ),
        (
            "sonar-default-effort",
            {
                "default": DEFAULT_EFFORT,
                "type": "int",
                "metavar": "<effort>",
                "help": "Number of effort minutes for rules not specified in"
                        " --sonar-rules."
            },
        ),
        (
            "sonar-default-type",
            {
                "default": DEFAULT_TYPE,
                "type": "string",
                "metavar": "<type>",
                "help": "Type of SonarQube issue for rules not specified in"
                        " --sonar-rules."
            },
        ),
    )


class SonarJSONReporter(BaseReporter):
    """Report messages and layouts in JSON that SonarQube can import."""

    __implements__ = IReporter
    name = "sonarjson"
    extension = "json"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.severities = {}
        self.efforts = {}
        self.types = {}
        self.default_severity = DEFAULT_SEVERITY
        self.default_effort = DEFAULT_EFFORT
        self.default_type = DEFAULT_TYPE

    def _parse_sonar_options(self):
        sonar_checker = _get_checker(self.linter, DummySonarRulesChecker)
        for sonar_rule in sonar_checker.option_value('sonar-rules'):
            split = sonar_rule.split(":")
            msg_id = self._validate_msg_id(split[0])
            if len(split) > 1:
                self.severities[msg_id] = self._validate_severity(split[1])
            if len(split) > 2:
                self.efforts[msg_id] = self._validate_effort(split[2])
            if len(split) > 3:
                self.types[msg_id] = self._validate_type(split[3])
        self.default_severity = sonar_checker.option_value('sonar-default-severity')
        self.default_effort = sonar_checker.option_value('sonar-default-effort')
        self.default_type = sonar_checker.option_value('sonar-default-type')

    def display_messages(self, layout: Optional[Section]):
        # Only parse the options now because self.linter is not available
        # in the constructor of BaseReporter (it is set later).
        self._parse_sonar_options()
        json_dumpable = [self._msg_to_sonar_dict(msg) for msg in self.messages]
        print(json.dumps({"issues": json_dumpable}, indent=4), file=self.out)

    def _msg_to_sonar_dict(self, msg: Message):
        sonar_dict = {
            "engineId": "PYLINT",
            "ruleId": msg.msg_id,
            "type": self.types.get(msg.msg_id, self.default_type),
            "primaryLocation": {
                "message": msg.msg or "",
                "filePath": msg.path,
                "textRange": {
                    "startLine": msg.line,
                    "startColumn": msg.column,
                }
            },
            "severity": self.severities.get(msg.msg_id, self.default_severity),
            "effortMinutes": self.efforts.get(msg.msg_id, self.default_effort)
        }
        if hasattr(msg, "endline") and msg.end_line:
            sonar_dict["primaryLocation"]["textRange"]["endLine"] = msg.end_line
        if hasattr(msg, "end_column") and msg.end_column:
            sonar_dict["primaryLocation"]["textRange"]["endColumn"] = msg.end_column
        return sonar_dict

    def _validate_msg_id(self, msg_id: str):
        emittable, _ = self.linter.msgs_store.find_emittable_messages()
        for msg in emittable:
            if msg_id == msg.msgid:
                return msg_id
        raise InvalidArgsError(f"{msg_id} is not a known message id.")

    @staticmethod
    def _validate_severity(severity: str):
        if severity in ALLOWED_SEVERITIES:
            return severity
        else:
            raise InvalidArgsError(f"{severity} is not one of {ALLOWED_SEVERITIES}.")

    @staticmethod
    def _validate_effort(effort: str):
        try:
            return int(effort)
        except ValueError:
            raise InvalidArgsError(f"{effort} is not an integer.")

    @staticmethod
    def _validate_type(msg_type: str):
        if msg_type in ALLOWED_TYPES:
            return msg_type
        else:
            raise InvalidArgsError(f"{msg_type} is not one of {ALLOWED_TYPES}.")

    def display_reports(self, layout: Section):
        pass

    def _display(self, layout: Section):
        pass


def register(linter: PyLinter):
    linter.register_reporter(SonarJSONReporter)
    linter.register_checker(DummySonarRulesChecker(linter))


def _get_checker(linter: PyLinter, checker_class):
    for checker in linter.get_checkers():
        if isinstance(checker, checker_class):
            return checker
    raise ValueError(f"Checker class {checker_class} not found.")
