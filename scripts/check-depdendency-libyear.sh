#!/bin/bash

set -ex

MAX_LIBYEARS=20

REQS_FILE=$(mktemp)

poetry export -f requirements.txt --output "${REQS_FILE}" --without-hashes
sed -i -e 's/; .*//g' "${REQS_FILE}"
LIVE_LIBYEARS=$(poetry run libyear -r "${REQS_FILE}" | grep "system is" | awk -F 'system is | libyears' '{print $2}')

if [ "${LIVE_LIBYEARS}" = 'up-to-date!' ]
then
  echo "System up to date!"
elif [[ $(echo "${LIVE_LIBYEARS} > ${MAX_LIBYEARS}" | bc -l) -eq "1" ]]
then
  echo "The live dependencies from requirements.txt are more than ${MAX_LIBYEARS} old. Please upgrade!"
  exit 1
fi

DEV_REQS_FILE=$(mktemp)
JUSTDEV_REQS_FILE=$(mktemp)

poetry export -f requirements.txt --output "${DEV_REQS_FILE}" --without-hashes --dev
sed -i -e 's/; .*//g' "${DEV_REQS_FILE}"
grep -Fvxf "${REQS_FILE}" "${DEV_REQS_FILE}"  > "${JUSTDEV_REQS_FILE}"

DEV_LIBYEARS=$(poetry run libyear -r "${JUSTDEV_REQS_FILE}" | grep "system is" | awk -F 'system is | libyears' '{print $2}')

if [ "${DEV_LIBYEARS}" = 'up-to-date!' ]
then
  echo "System up to date!"
elif [[ $(echo "${DEV_LIBYEARS} > ${MAX_LIBYEARS}" | bc -l) -eq "1" ]]
then
  echo "The dev dependencies from dev-requirements.txt are more than ${MAX_LIBYEARS} old. Please upgrade!"
  exit 1
fi
