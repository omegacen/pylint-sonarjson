# pylint-sonarjson

A PyLint plugin that can output to [SonarQube-importable JSON](https://docs.sonarqube.org/latest/analysis/generic-issue/).

## Usage

```
$ pylint \
    --load-plugins=pylint_sonarjson \
    --output-format=sonarjson \
    --sonar-rules=<msg_id:severity[:effort[:type]]>,... \
    --sonar-default-severity=<severity> \
    --sonar-default-effort=<effort> \
    --sonar-default-type=<type> \
    [...]
```

The plugin provides a new option `sonar-rules` that can configure the severity, 
effort,  and type of the issue as it would appear in SonarQube. The option takes
a comma-separated list whose items are of the form `<msg_id>:<severity>:<effort>:<type>`.
The message ID and severity are required; the effort and type are optional and
may be omitted.

In addition, the default severity, effort, and type for messages that are not listed
in `sonar-rules` can respectively be set with `sonar-default-severity`, 
`sonar-default-effort`, `sonar-default-type`. They default to `MINOR`, `5`, and
`CODE_SMELL` respectively.

For example:

```
$ pylint \
    --load-plugins=pylint_sonarjson \
    --output-format=sonarjson \
    --sonar-rules=C0114:INFO:10,C0328:MINOR:1 \
    my_file.py
```

Output:

```json
{
    "issues": [
        {
            "engineId": "PYLINT",
            "ruleId": "C0114",
            "type": "CODE_SMELL",
            "primaryLocation": {
                "message": "Missing module docstring",
                "filePath": "my_file.py",
                "textRange": {
                    "startLine": 1,
                    "startColumn": 0
                }
            },
            "severity": "INFO",
            "effortMinutes": 10
        }
    ]
}
```


## Installation

```
pip install pylint-sonarjson
```
