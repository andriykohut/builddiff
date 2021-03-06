# builddiff
[![travis](https://travis-ci.org/andriykohut/builddiff.png)](https://travis-ci.org/andriykohut/builddiff)

Compare console output of Jenkins builds

## Usage
Console output example:
```
...
  62) some-test-file.js Some test case:
     TypeError: Object mouse has no method 'tail'
  63) some-test-file.js Another test case:
     TypeError: Object mouse has no method 'tail'
  63) another-test-file.js Yet Another test case:
     TypeError: Object mouse has no method 'tail'
...
```
Let's try:
```bash
bd -r "^\s+\d+\)\s(?P<key>[\w|\-]+\.js)\s(?P<values>.+):$" -f "I|M" list 589
bd -r "^\s+\d+\)\s(?P<key>[\w|\-]+\.js)\s(?P<values>.+):$" -f "I|M" diff 589 590 --color
bd list 16475 16476 16477 16478 16479 16480 16481 16482
```
The last one lists failures for multiple builds and uses default regex and flags

Here how it works:
```
usage: bd [-h] [-c CONFIG] [-f FLAGS] [-r RE] [-k KEY_GROUP] [-v VALUES_GROUP]
          {diff,list} ...

positional arguments:
  {diff,list}           commands

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        A path to configuration file [Default: ~/.bdiff]
  -f FLAGS, --flags FLAGS
                        Python regex flags, eg: "I" or "I|M" [Default: I|M]
  -r RE, --re RE        Regex for parsing console output. [Default:
                        ^\s+\d+\)\s(?P<key>[\w|\-]+\.js)\s(?P<values>.+):$]
  -k KEY_GROUP, --key KEY_GROUP
                        key group name [Default: key]
  -v VALUES_GROUP, --values VALUES_GROUP
                        values group name [Default: values]
```
## Installation
```
virtualenv myenv
source myenv/bin/activate
pip install git+git://github.com/andriykohut/builddiff

bd -h
```
## Config
You will be prompted for configuration first time you run `bd`.
Here's how config looks like:
```yaml
cat ~/.bdiff
jenkins:
  url: <jenkins-host>
  job: <jenkins-job-name>
  user: <jenkins-user>
  password: <jenkins-password>
```
## Authors

`builddiff` was written by [Andriy Kogut](mailto:kogut.andriy@gmail.com).
