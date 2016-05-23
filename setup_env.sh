#!/bin/bash

GS_TOP=$(cd $(dirname $0) && pwd)
export PATH=$GS_TOP/bin:$PATH
export PYTHONPATH=${PYTHONPATH}${PYTHONPATH:+:}$GS_TOP

bash -i

