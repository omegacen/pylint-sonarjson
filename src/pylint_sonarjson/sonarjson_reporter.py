import json
from typing import Optional, List

from pylint.interfaces import IReporter
from pylint.message import Message
from pylint.reporters.base_reporter import BaseReporter
from pylint.reporters.ureports.nodes import Section
from pylint_plugin_utils import get_checker

from .sonaroptions_checker import SonarOptionsChecker


class SonarJSONReporter(BaseReporter):
    """Report messages and layouts in JSON that SonarQube can import."""

    __implements__ = IReporter
    name = "sonarjson"
    extension = "json"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._checker: Optional[SonarOptionsChecker] = None
        self._messages: List[Message] = []

    def handle_message(self, msg: Message) -> None:
        self._messages.append(msg)

    @property
    def sonar_checker(self) -> SonarOptionsChecker:
        if not self._checker:
            self._checker = get_checker(self.linter, SonarOptionsChecker)
        return self._checker

    def display_messages(self, layout: Optional[Section]):
        json_dumpable = [self._msg_to_sonar_dict(msg) for msg in self._messages]
        print(json.dumps({"issues": json_dumpable}, indent=4), file=self.out)

    def _msg_to_sonar_dict(self, msg: Message):
        sonar_dict = {
            "engineId": "PYLINT",
            "ruleId": msg.msg_id,
            "type": self.sonar_checker.type(msg),
            "primaryLocation": {
                "message": msg.msg or "",
                "filePath": msg.path,
                "textRange": {
                    "startLine": msg.line,
                    "startColumn": msg.column,
                }
            },
            "severity": self.sonar_checker.severity(msg),
            "effortMinutes": self.sonar_checker.effort(msg)
        }
        if hasattr(msg, "end_line") and msg.end_line:
            sonar_dict["primaryLocation"]["textRange"]["endLine"] = msg.end_line
        if hasattr(msg, "end_column") and msg.end_column:
            sonar_dict["primaryLocation"]["textRange"]["endColumn"] = msg.end_column
        return sonar_dict

    def display_reports(self, layout: Section):
        pass

    def _display(self, layout: Section):
        pass
