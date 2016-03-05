#!/bin/bash

readonly DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
pushd "${DIR}"
node "${DIR}/start-server.js" -f default-config.json
popd
