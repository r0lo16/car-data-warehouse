# DevOps i Backend - stan wdrozenia

## Dostepne komponenty
- VPS OVH configured
- Docker + Docker Compose installed
- PostgreSQL running in container
- FastAPI running in container
- FastAPI exposed by DuckDNS + Nginx Proxy Manager

## Endpoint status
Working endpoint:
- `GET /health`

Expected response:
```json
{
  "status": "ok",
  "service": "car-data-warehouse-api"
}
```

## Operational rules in team
- VPS is managed by Dawid
- other team members work locally
- no SSH sharing
- no local edits of infra config without prior agreement

## Protected areas (do not change without agreement)
- `backend/`
- `docker-compose.yml`
- `.env` / secrets
- VPS, DuckDNS, Nginx Proxy Manager configuration
