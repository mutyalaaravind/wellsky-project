#!/bin/bash

set -e

# Extract query args
eval "$(jq -r '@sh "OKTA_API_TOKEN=\(.okta_api_token) EMAIL=\(.email)"')"

USER_ID=`curl -s "https://wellsky-ciam.oktapreview.com/api/v1/users?search=profile.email+eq+%22${EMAIL}%22" -H "Authorization: SSWS ${OKTA_API_TOKEN}" | jq -r '.[0].id'`
echo '{"user_id": "'$USER_ID'"}'
