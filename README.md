# pylint-sonarjson

A PyLint plugin that can output to [SonarQube-importable JSON](https://docs.sonarqube.org/latest/analysis/generic-issue/).

## Usage

```
$ pylint --load-plugins=pylint_sonarjson --output-format=sonarjson \
    --sonar-rules=<msg_id:severity[:effort[:type]]>,... \
    --sonar-default-severity=<severity> \
    --sonar-default-effort=<effort> \
    --sonar-default-type=<type> \
    [...]
```

For example:

```
$ pylint --load-plugins=pylint_sonarjson --output-format=sonarjson --sonar-rules=C0114:INFO:10,C0328:MINOR:1
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
