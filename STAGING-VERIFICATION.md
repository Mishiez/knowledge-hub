# F4 Staging Verification

This document is an evidence checklist for Track F4: zero-downtime deployment, observable logs, health monitoring, PostgreSQL backups, and restore verification.

Run the server commands on the Droplet unless a section says to run them locally.

## 1. Check Running Services

Run on the Droplet:

```bash
cd ~/knowledge-hub-staging

docker compose -f docker-compose.staging.yml ps
```

Expected services:

```text
backend-blue    healthy
backend-green   healthy
staging-db      healthy
frontend        Up
```

This proves that both backend replicas, PostgreSQL, and the Nginx frontend container are running.

## 2. Check Backend Health Directly

```bash
docker inspect \
  --format '{{.Name}} {{.State.Health.Status}}' \
  knowledge-hub-staging-backend-blue-1 \
  knowledge-hub-staging-backend-green-1
```

Expected:

```text
/knowledge-hub-staging-backend-blue-1 healthy
/knowledge-hub-staging-backend-green-1 healthy
```

This proves Docker is evaluating the backend health checks and both replicas are healthy.

## 3. Check API, Frontend, HTTPS, and Redirect

```bash
curl -sk -o /dev/null -w 'API HTTPS: %{http_code}\n' \
  https://mish-knowledge-hub.duckdns.org/api/posts/

curl -sk -o /dev/null -w 'Frontend HTTPS: %{http_code}\n' \
  https://mish-knowledge-hub.duckdns.org/

curl -sI http://mish-knowledge-hub.duckdns.org/ | \
  grep -Ei 'HTTP/|location:'

curl -skI https://mish-knowledge-hub.duckdns.org/ | \
  grep -Ei 'HTTP/|strict-transport-security'
```

Expected:

```text
API HTTPS: 200
Frontend HTTPS: 200
HTTP/1.1 301 Moved Permanently
Location: https://mish-knowledge-hub.duckdns.org/
HTTP/1.1 200 OK
```

This proves the API and frontend are available over HTTPS and HTTP redirects to HTTPS.

## 4. Show Nginx Routes Through Both Replicas

```bash
docker compose -f docker-compose.staging.yml exec -T frontend \
  nginx -T 2>&1 | grep -A5 -B2 'backend_pool'
```

Expected configuration:

```nginx
upstream backend_pool {
    server backend-blue:8000;
    server backend-green:8000;
}
```

This proves Nginx can route API and admin traffic through both backend replicas.

## 5. Show Accessible Logs

```bash
docker compose -f docker-compose.staging.yml logs \
  --tail=50 backend-blue backend-green frontend
```

This proves the service logs are accessible centrally through Docker Compose.

## 6. Search Logs for Errors Quickly

```bash
docker compose -f docker-compose.staging.yml logs --no-color \
  backend-blue backend-green frontend | \
  grep -iE 'error|exception|failed|critical' || \
  echo "No matching errors found"
```

If no errors are present, the command prints:

```text
No matching errors found
```

If an error is present, the matching log lines are printed. This demonstrates that an operator can search the combined service logs quickly.

## 7. Prove Docker Log Rotation

```bash
docker inspect knowledge-hub-staging-backend-blue-1 \
  --format '{{json .HostConfig.LogConfig}}'
```

Expected:

```json
{"Type":"json-file","Config":{"max-file":"5","max-size":"10m"}}
```

This proves each Docker log file is limited to 10 MB and Docker retains at most five rotated files.

## 8. Show Zero-Downtime Evidence

```bash
cd ~/knowledge-hub-staging

grep -Ev 'status=200$' deployment-smoke.log || \
  echo "No failed requests"

grep -c 'status=200$' deployment-smoke.log

grep -E 'status=(000|502|503|504)$' deployment-smoke.log || \
  echo "No connection or gateway failures"
```

Expected evidence from the completed test:

```text
No failed requests
360
No connection or gateway failures
```

This proves that all 360 recorded requests returned HTTP 200, with no connection failures or common gateway errors during deployment testing.

## 9. Show the Backup and Checksum

```bash
ls -lh backups
sha256sum -c backups/*.dump.sha256
```

Expected:

```text
/root/knowledge-hub-staging/backups/knowledgehub-20260910T075422Z.dump: OK
```

This proves a PostgreSQL backup exists and its SHA-256 checksum is valid.

## 10. Show Automatic Backup Scheduling

```bash
crontab -l
```

Expected cron entry:

```cron
30 2 * * * /root/knowledge-hub-staging/ops/backup-staging-db.sh >> /root/knowledge-hub-staging/backup.log 2>&1
```

Show backup activity when the log exists:

```bash
tail -n 20 /root/knowledge-hub-staging/backup.log
```

The schedule runs the backup every day at 02:30 and redirects its output to `backup.log`.

## 11. Show Restore Evidence

The restore was performed against a temporary database named `knowledgehub_restore`, not the live staging database. The temporary database was removed after verification.

Show the backup and checksum again:

```bash
ls -lh backups
sha256sum -c backups/*.dump.sha256
```

Present the recorded restore result to the mentor:

```text
14 tables restored
users: 9
posts: 7
comments: 6
likes: 0
temporary knowledgehub_restore database removed
```

This proves that the backup was restored successfully and that the recovered tables contained application data. The live staging database was not modified by the restore test.

## F4 Evidence Summary

Items 1–11 prove:

- The deployed services are running and healthy.
- HTTPS and HTTP-to-HTTPS redirect work.
- Nginx routes traffic through both backend replicas.
- Logs are centrally accessible and searchable.
- Docker log rotation is configured.
- Continuous deployment requests completed without client-visible failures.
- PostgreSQL backups exist and pass checksum validation.
- Daily backup scheduling is configured.
- A real restore was completed and verified in an isolated database.
