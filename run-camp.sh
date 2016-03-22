#!/bin/bash
#
# Play hunter vs mastermind many times.
#
# USAGE: <SCRIPT> <NUMBER OF GAMES>
#

# Number of games to play
GAMES="${1}"
if [ -z "${GAMES}" ]; then
  GAMES=1
fi

#readonly MYAI="hunter"
#readonly MYAI="memory"
#readonly MYAI="mrtwo"
#readonly MYAI="ritari"
#readonly MYAI="minradar"
#readonly MYAI="goodradar"
#readonly MYAI="superb"
readonly MYAI="winwin"

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

# Single game loop
play() {
  pushd "${DIR}"
  # Start server
  pushd server
  #node "./start-server.js" -f default-config.json -o false -d 1000 -l game.json > run-server.log 2>run-server.err &
  #node "./start-server.js" -f default-config.json -o false -l game.json > run-server.log 2>run-server.err &
  node "./start-server.js" -f default-config.json -o true -l game.json > run-server.log 2>run-server.err &
  #node "./start-server.js" -f asteroid-default-config.json -o false -d 1000 -l game.json > run-server.log 2>run-server.err &
  sleep 1
  popd
  # Start AI 1
  #pushd ./clients/javascript
  #node "./cli.js" --ai mastermind 2>&1 > /dev/null &
  pushd ./clients/python
  activate
  #python "./cli.py" --ai camp --name camp 2>&1 > /dev/null &
  #python "./cli.py" --ai dummy --name dummy 2>&1 > /dev/null &
  #python "./cli.py" --ai hunter --name hunter 2>&1 > /dev/null &
  #python "./cli.py" --ai memory --name memory 2>&1 > /dev/null &
  python "./cli.py" --ai goodradar --name goodradar 2>&1 > /dev/null &
  popd
  # Start AI 2
  pushd ./clients/python
  activate
  if [ ${GAMES} -ge 2 ]; then
    python "./cli.py" --ai "${MYAI}" --name "${MYAI}" >> "${DIR}/${GAMELOG}" 2>> "${DIR}/${GAMEERR}"
  else
    python "./cli.py" --ai "${MYAI}" --name "${MYAI}"
  fi
  popd
  popd
}

# Save the results
if [ ${GAMES} -ge 2 ]; then
    RESULT_FOLDER="results-$(date +"%y%m%y-%H%M%S")"
    mkdir "${RESULT_FOLDER}"
fi

# Loop the games
COUNTER=1
while [  ${COUNTER} -le ${GAMES} ]; do
  echo "GAME ${COUNTER}"
  play
  if [ ${GAMES} -ge 2 ]; then
      sleep 0.1
      GAME_JSON="${RESULT_FOLDER}/game.json"
      # Get the log
      mv "${DIR}/server/game.json" "${GAME_JSON}"
      # Make the json prettier
      python -m json.tool "${GAME_JSON}" > "${RESULT_FOLDER}/game-${COUNTER}.json"
      rm "${GAME_JSON}"
  fi
  let COUNTER=COUNTER+1 
done

# Print/save the results
if [ ${GAMES} -ge 2 ]; then
    WON=$(grep "Game ended. You win" "${GAMEERR}" | wc -l)
    PERCENT=$(bc <<< "scale=2; ${WON}/${GAMES}*100")

    echo "WON: ${WON} / ${GAMES}, ${PERCENT}" | tee "${RESULT_FOLDER}/overall.txt"
fi
