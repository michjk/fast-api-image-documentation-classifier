#!/usr/bin/env sh
set -eu

: "${GARAGE_ADMIN_ENDPOINT:=http://127.0.0.1:3902}"
: "${GARAGE_BUCKET:=doc-images}"
: "${GARAGE_LAYOUT_ZONE:=local}"
: "${GARAGE_LAYOUT_CAPACITY:=100G}"

echo "Fetching Garage node ID..."
NODE_ID="$(docker compose exec -T garage /usr/bin/garage node id -q | tail -n 1)"

echo "Assigning node ${NODE_ID} to layout..."
docker compose exec -T garage /usr/bin/garage layout assign -z "${GARAGE_LAYOUT_ZONE}" -c "${GARAGE_LAYOUT_CAPACITY}" "${NODE_ID}"
docker compose exec -T garage /usr/bin/garage layout apply --version 1

echo "Creating API key..."
KEY_INFO="$(docker compose exec -T garage /usr/bin/garage key create app-key)"
ACCESS_KEY_ID="$(printf "%s" "${KEY_INFO}" | awk '/Key ID/ {print $3}')"
SECRET_ACCESS_KEY="$(printf "%s" "${KEY_INFO}" | awk '/Secret key/ {print $3}')"

echo "Creating bucket ${GARAGE_BUCKET}..."
docker compose exec -T garage /usr/bin/garage bucket create "${GARAGE_BUCKET}" || true

echo "Granting permissions..."
docker compose exec -T garage /usr/bin/garage bucket allow --read --write --owner "${GARAGE_BUCKET}" --key "${ACCESS_KEY_ID}"

echo "Garage initialized."
echo "S3 endpoint: http://127.0.0.1:3900"
echo "Bucket: ${GARAGE_BUCKET}"
echo "Access key id: ${ACCESS_KEY_ID}"
echo "Secret access key: ${SECRET_ACCESS_KEY}"
