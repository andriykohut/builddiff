# builddiff

![https://travis-ci.org/andriykohut/builddiff](https://travis-ci.org/andriykohut/builddiff.png)


Compate console output of Jenkins builds

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
```
bdiff 167 101 -r "^\s+\d+\)\s(?P<test_file>[\w|\-]+\.js)\s(?P<test_case>.+):$" -f "I|M"

```
Here how it works:
```
bdiff -h
usage: bdiff [-h] [-c CONFIG] [-f FLAGS] [-r RE] A B

positional arguments:
  A                     build A (good)
  B                     build B (bad)

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        A path to configuration file [Default: ~/.bdiff]
  -f FLAGS, --flags FLAGS
                        Python regex flags, eg: "I" or "I|M"
  -r RE, --re RE        Regex for parsing console output
```
## Installation
```
virtualenv myenv
source myenv/bin/activate
pip install git+git://github.com/andriykohut/builddiff

bdiff -h
```
## Authors

`builddiff` was written by [Andriy Kogut](mailto:kogut.andriy@gmail.com).
