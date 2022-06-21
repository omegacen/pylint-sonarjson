from typing import Dict, Set
from sys import stderr

from pylint.checkers import BaseChecker
from pylint.exceptions import InvalidArgsError
from pylint.interfaces import IAstroidChecker
from pylint.message import Message

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


class SonarOptionsChecker(BaseChecker):
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
        (
            "only-enable-sonar-rules",
            {
                "default": False,
                "type": "yn",
                "metavar": "<y or n>",
                "help": "Only enable messages specified in --sonar-rules."
            },
        ),
        (
            "halt-on-invalid-sonar-rules",
            {
                "default": True,
                "type": "yn",
                "metavar": "<y or n>",
                "help": "If enabled, an exception will be raised if a"
                        " non-existing rule is given in --sonar-rules and the "
                        " plugin will halt."
                        " When disabled, non-existing rules will be"
                        " reported on stderr but are otherwise ignored."
            }
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._msg_ids: Set[str] = set()
        self._severities: Dict[str, str] = {}
        self._efforts:  Dict[str, int] = {}
        self._types:  Dict[str, str] = {}

    def severity(self, msg: Message):
        return self._severities.get(msg.msg_id, self.option_value('sonar-default-severity'))

    def effort(self, msg: Message):
        return self._efforts.get(msg.msg_id, self.option_value('sonar-default-effort'))

    def type(self, msg: Message):
        return self._types.get(msg.msg_id, self.option_value('sonar-default-type'))

    def load_configuration(self):
        for sonar_rule in self.option_value('sonar-rules'):
            self._parse_sonar_rule(sonar_rule)
        if self.option_value('only-enable-sonar-rules'):
            self._only_enable_sonar_rules()

    def _parse_sonar_rule(self, sonar_rule: str):
        split = sonar_rule.split(":")
        msg_id = split[0]
        if not self._is_valid_msg_id(msg_id):
            if self.option_value('halt-on-invalid-sonar-rules'):
                raise InvalidArgsError(f"{msg_id} is not a known Pylint message id.")
            else:
                print(f"Disabling {msg_id} since it is not a known Pylint message id.", file=stderr)
                return
        self._msg_ids.add(msg_id)
        if len(split) > 1:
            self._severities[msg_id] = self._validate_severity(split[1])
        if len(split) > 2:
            self._efforts[msg_id] = self._validate_effort(split[2])
        if len(split) > 3:
            self._types[msg_id] = self._validate_type(split[3])

    def _only_enable_sonar_rules(self):
        if not hasattr(self.linter.msgs_store, 'find_emittable_messages'):
            raise InvalidArgsError(f"Pylint version is too low to use only-enable-sonar-rules.")
        emittable, _ = self.linter.msgs_store.find_emittable_messages()
        for msg in emittable:
            self.linter.disable(msg.msgid)
        for msg_id in self._msg_ids:
            self.linter.enable(msg_id)

    def _is_valid_msg_id(self, msg_id: str):
        if not hasattr(self.linter.msgs_store, 'find_emittable_messages'):
            return True
        emittable, _ = self.linter.msgs_store.find_emittable_messages()
        for msg in emittable:
            if msg_id == msg.msgid:
                return True
        return False

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
