#!/bin/bash

readonly DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
pushd "${DIR}"
node "${DIR}/cli.js" --ai mastermind
popd
