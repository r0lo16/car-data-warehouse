# Agile / Scrum + Kanban

Project management is done in Trello.

## Board columns
- Product Backlog
- Sprint 1 - Projektowanie
- Sprint 2 - ETL i baza
- Sprint 2.5 - DevOps i Backend API
- Sprint 3 - Dashboard
- In Progress
- Review / Testy
- Done

## Team roles
- Dawid: Data Architect / DevOps Engineer / Backend Developer / Scrum Master
- Kuba: Data Engineer (ETL + NBP currency API)
- Mateusz: BI Developer / SQL / Dashboard

## Git process
Rules:
- do not push directly to `main`
- all changes through Pull Request
- `main` stays stable and protected

Standard flow:
1. update `main`
2. switch/create own branch
3. implement task
4. local test
5. commit + push
6. PR to `main`
7. review and merge by Dawid

## Definition of Done
Task is done when:
- it works locally
- has commit and pushed branch
- PR exists with change description and test note
- docs are updated (if needed)
- no secrets were committed
- change can be verified by Dawid
