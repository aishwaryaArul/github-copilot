# Unit Test Case Documentation

The suite is run with `pytest -q` and uses temporary SQLite databases so tests are isolated and deterministic.

| Test area | Covered behavior |
|---|---|
| Project creation | Persists a project, generates an ID, applies the active default, and preserves tenant ID. |
| Project status | Updates status for the owning tenant and rejects missing projects. |
| Project team lookup | Returns only matching teams within the requested tenant and preserves ID order. |
| Project deletion | Deletes an owned project and rejects missing or cross-tenant projects. |
| Project validation | Rejects blank project names and teams. |
| Audit persistence | Stores tenant, actor, action, resource, details, and timestamp. |
| Audit isolation | Limits audit results to the requested tenant and honors result limits. |
| Notification creation/listing | Stores notifications and restricts results by tenant and recipient. |
| Notification read state | Marks only the addressed tenant recipient's notification as read. |
| Core validation | Rejects blank values and invalid result limits. |
| API authorization | Rejects audit requests without the required tenant header. |
| API workflows | Covers notification create, list, and mark-read endpoints. |

Known gaps are authentication-backed tenant identity, automatic milestone-triggered notification dispatch, migration testing for existing databases, and concurrent transaction tests.