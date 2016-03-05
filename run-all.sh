#!/bin/bash
#
# Play hunter vs mastermind many times.
#
# USAGE: <SCRIPT> <GAMES>
#

GAMES="${1}"
if [ -z "${GAMES}" ]; then
  GAMES=1
fi

readonly DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
readonly GAMELOG="games.log"
readonly GAMEERR="games.err"

if [ -f "${GAMELOG}" ]; then
  rm "${GAMELOG}"
fi
if [ -f "${GAMEERR}" ]; then
  rm "${GAMEERR}"
fi

# Activate virtualenv for Python client
activate() {
  source venv/bin/activate
}

play() {
  pushd "${DIR}"
  pushd server
  ./run-server.sh > run-server.log 2>run-server.err &
  sleep 1
  popd
  pushd ./clients/javascript
  ./mastermind.sh 2>&1 > /dev/null &
  sleep 1
  popd
  pushd ./clients/python
  activate
  ./hunter.sh >> "${DIR}/${GAMELOG}" 2>> "${DIR}/${GAMEERR}"
  popd
  popd
}

COUNTER=1
while [  ${COUNTER} -le ${GAMES} ]; do
  echo "GAME ${COUNTER}"
  play
  let COUNTER=COUNTER+1 
done

WON=$(grep "Game ended. You win" "${GAMEERR}" | wc -l)
PERCENT=$(bc <<< "scale=2; ${WON}/${GAMES}*100")

echo "WON: ${WON} / ${GAMES}, ${PERCENT}"