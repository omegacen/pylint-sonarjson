# pylint-sonarjson

A PyLint plugin that can output to [SonarQube-importable JSON](https://docs.sonarqube.org/latest/analysis/generic-issue/)
with configurable issue severity, effort, and type. 

This is useful because when importing PyLint's 
[parsable output](https://pylint.pycqa.org/en/latest/user_guide/output.html#output-options)
via [SonarQube mechanism for third-party issues](https://docs.sonarqube.org/latest/analysis/external-issues/)
all the severities are set to `MAJOR`. With `pylint-sonarjson` you can configure the
issue severity per PyLint message ID, and import that as generic JSON in SonarQube.

## Usage

```
$ pylint \
    --load-plugins=pylint_sonarjson \
    --output-format=sonarjson \
    --sonar-rules=<msg_id>:<severity>[:<effort>[:<type>]],... \
    --sonar-default-severity=<severity> \
    --sonar-default-effort=<effort> \
    --sonar-default-type=<type> \
    --only-enable-sonar-rules=<y or n> \
    --halt-on-invalid-sonar-rules=<y or n> \
    [...]
```

The plugin provides a new option `sonar-rules` that can configure the severity, 
effort, and type of the issue as it would appear in SonarQube. The option takes
a comma-separated list whose items are of the form `<msg_id>:<severity>:<effort>:<type>`.
The effort and type are optional and  may be omitted.

In addition, the default severity, effort, and type for messages that are not listed
in `sonar-rules` can respectively be set with `sonar-default-severity`, 
`sonar-default-effort`, `sonar-default-type`. They default to `MINOR`, `5`, and
`CODE_SMELL` respectively.

Setting the option `only-enable-sonar-rules` to `y` disables all messages
except for those specified in `sonar-rules`. It is equivalent to 
`--disable=all --enable=<msg_id>,...` where `<msg_id>,...` are the message IDs
specified in `sonar-rules`. The default value of `only-enable-sonar-rules` is `n`.

Lastly, enabling the option `halt-on-invalid-sonar-rules` will cause the plugin
to raise an exception when a rule given in `sonar-rules` does not exist in Pylint
and halt. Disabling this option will instead only report the invalid rule on
stderr but will otherwise ignore the invalid rule. The default value of 
`halt-on-invalid-sonar-rules` is `y`.`

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

This output, when saved to a file, can be imported into SonarQube as follows:

```
$ sonar-scanner -Dsonar.externalIssuesReportPaths=<path_to_pylint_sonarjson_log>
```

## Installation

```
pip install pylint-sonarjson
```
