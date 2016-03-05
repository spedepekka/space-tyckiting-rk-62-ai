#!/bin/bash

readonly DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
pushd "${DIR}"
python "${DIR}/cli.py" --ai hunter --name hunter
popd
