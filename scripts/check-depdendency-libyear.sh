#!/bin/bash

set -ex

MAX_LIBYEARS=20

LIVE_LIBYEARS=$(libyear -r requirements.txt | grep "system is" | awk -F 'system is | libyears' '{print $2}')

if [ "${LIVE_LIBYEARS}" = 'up-to-date!' ]
then
  echo "System up to date!"
elif [[ $(echo "${LIVE_LIBYEARS} > ${MAX_LIBYEARS}" | bc -l) -eq "1" ]]
then
  echo "The live dependencies from requirements.txt are more than ${MAX_LIBYEARS} old. Please upgrade!"
  exit 1
fi

DEV_LIBYEARS=$(libyear -r requirements-dev.txt | grep "system is" | awk -F 'system is | libyears' '{print $2}')

if [ "${DEV_LIBYEARS}" = 'up-to-date!' ]
then
  echo "System up to date!"
elif [[ $(echo "${DEV_LIBYEARS} > ${MAX_LIBYEARS}" | bc -l) -eq "1" ]]
then
  echo "The dev dependencies from dev-requirements.txt are more than ${MAX_LIBYEARS} old. Please upgrade!"
  exit 1
fi
