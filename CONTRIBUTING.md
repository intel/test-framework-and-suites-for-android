# Contributing guidelines

If you have improvements, send us your pull requests! For those
just getting started, Github has a [howto](https://help.github.com/articles/using-pull-requests/).

Our team members will be assigned to review your pull requests. Once the pull requests are approved and pass continuous integration checks, we will merge the pull requests.


### Pull Request Checklist

Before sending your pull requests, make sure you followed this list.

* Read [contributing guidelines](CONTRIBUTING.md).
* Change are consisent with the [Coding Style](#coding-style).
* Make sure your contributed Test Case has been executed and validated.
* Run [framework sanity check test](#running-sanity-check)


### Coding Style

* Follow [PEP8](https://www.python.org/dev/peps/pep-0008) coding style, with one excpetion: *max line length is 120*.
* Each python file (except empty `__init__.py`) should have **Apache License 2.0** header declaration.

Standard License Header template:
```python
'''
Copyright [yyyy] [name of copyright owner]

Licensed under the Apache License, Version 2.0 (the "License"); 
you may not use this file except in compliance with the License. 
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software 
distributed under the License is distributed on an "AS IS" BASIS, 
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. 
See the License for the specific language governing permissions and 
limitations under the License.
'''
```
##### Git Hooks
Git hooks to check coding style, run below to setup environment:
```bash
# in code root
ln –s ../../.git-hooks/pre-commit .git/hooks/pre-commit
sudo pip install flake8 autopep8  # make sure autopep8 & flake8 installed
```
It will be trigger and check coding style when you commit the code in local.

### Running sanity check
First, make sure you have already [install the depedencies](acs_setup_manager/README.md).

Then:
```
bash acs_test_suites/ACS_CI/run_test.sh
```
This will run ACS framework sanity testing. Make sure the result is *PASSED*:
```
ACS OUTCOME: SUCCESS
```
