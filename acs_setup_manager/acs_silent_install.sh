#!/bin/bash
##########################################################
# Copyright (C) 2018 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions
# and limitations under the License.
#
#
# SPDX-License-Identifier: Apache-2.0
###########################################################

if [ $(id -u) -ne 0 ]; then
  echo "Unable to install: you must run this script as root"
  exit 1
fi

is_python_supported()
{
  V1=2
  V2=7
  PY_V1=`python -V 2>&1|awk '{print $2}'|awk -F '.' '{print $1}'`
  PY_V2=`python -V 2>&1|awk '{print $2}'|awk -F '.' '{print $2}'`
  if [[ $PY_V1 -eq $V1 && $PY_V2 -eq $V2 ]]; then
    return 0
  else
    return 1
  fi
}

python --version
if [ $? -ne 0 ]; then
  echo Please install a supported python version 2.7.x
  exit 1
else
  py_support=`is_python_supported`
  if [[ $py_support -ne 0 ]]; then
    echo Please install a supported python version 2.7.x
    exit 1
  fi
fi

echo installing pip ...
apt-get update -y
apt-get install python-pip -y
if [ $? -ne 0 ]; then
  echo Error during install
  exit 1
fi

echo installing python libraries ...
pip install -U pip
cd "$(dirname "$0")"
pip install -r ./pip_requirements.txt
if [ $? -ne 0 ]; then
  echo Error during install
  exit 1
fi
