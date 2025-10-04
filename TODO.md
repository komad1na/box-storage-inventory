# TODO — Future improvements & features

## UX / UI

- Add confirm undo for deletions instead of immediate cascade
- Implement pagination for large datasets
- Add column sorting in tables
- Improve accessibility (keyboard navigation, larger contrast options)

## Functionality

- Export/Import CSV and JSON for boxes & items
- Add image attachments for items (store paths or blob in DB)
- Add tags and categories for items
- Add quantity history (transactions) and audit log
- Add bulk operations (bulk import, bulk delete)

## Persistence & API

- Add an optional remote sync backend (REST API)
- Add user authentication and roles (admin, read-only)
- Migrate to SQLAlchemy for more flexible queries & migrations

## Tests & CI

- Add CI pipeline to run tests on push (GitHub Actions)
- Add UI integration tests (screenshot diff tests)
- Add more edge-case tests (SQL errors, DB lock handling)

## Packaging

- Provide a packaged binary for Windows/Mac/Linux (PyInstaller / Briefcase)
- Provide an installer or portable build

## Analytics & Reporting

- Add simple reports: stock by box, low-stock alerts
- Add scheduled backups of the database
