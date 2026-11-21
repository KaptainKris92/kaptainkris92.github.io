#!/bin/sh
# Runs every minute from cron on the Mac mini. When main has a new commit,
# it rebuilds and restarts the site container. Pulling (instead of a
# self-hosted Actions runner) keeps this public repo's workflows off the server.
set -eu
cd "$(dirname "$0")/.."

exec 9>/tmp/kreations-deploy.lock
flock -n 9 || exit 0

git fetch -q origin main
new=$(git rev-parse origin/main)
[ "$new" = "$(cat deploy/.deployed 2>/dev/null)" ] && exit 0

echo "$(date -Is) deploying $new"
git reset -q --hard "$new"
docker compose -f deploy/docker-compose.yml up -d --build --remove-orphans

for i in $(seq 1 15); do
  if curl -fsS -o /dev/null http://127.0.0.1:8020/privacy.html; then
    echo "$new" > deploy/.deployed
    docker image prune -f --filter label=app=kreations >/dev/null
    echo "$(date -Is) live"
    exit 0
  fi
  sleep 2
done
echo "$(date -Is) site did not come up" >&2
exit 1
