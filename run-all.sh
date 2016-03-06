#!/bin/bash
#
# Play hunter vs mastermind many times.
#
# USAGE: <SCRIPT> <NUMBER OF GAMES>
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
  node "./start-server.js" -f default-config.json -o true > run-server.log 2>run-server.err &
  sleep 0.5
  popd
  pushd ./clients/javascript
  node "./cli.js" --ai mastermind 2>&1 > /dev/null &
  #pushd ./clients/python
  #activate
  #python "./cli.py" --ai camp --name camp 2>&1 > /dev/null &
  popd
  pushd ./clients/python
  activate
  python "./cli.py" --ai hunter --name hunter >> "${DIR}/${GAMELOG}" 2>> "${DIR}/${GAMEERR}"
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
