#!/bin/bash

activate() {
  source venv/bin/activate
}

readonly DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
pushd "${DIR}"
pushd server
./run-server.sh > run-server.log 2>run-server.err &
popd
pushd ./clients/javascript
./mastermind.sh 2>&1 > /dev/null &
popd
pushd ./clients/python
activate
./hunter.sh
popd
popd
