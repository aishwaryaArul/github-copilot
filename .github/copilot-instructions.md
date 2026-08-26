# Project Standards

## Technology Stack

- Backend: Python with FastAPI, served by Uvicorn.
- Testing: pytest with `fastapi.testclient.TestClient`.
- Frontend: plain HTML, CSS, and browser JavaScript under `src/static/`.
- Dependencies are managed in `requirements.txt`; do not add a framework or package without a clear task-specific reason.

## Architecture Conventions

- `src/app.py` owns the FastAPI application, in-memory activity data, API routes, and static-file mounting.
- The root route redirects to `/static/index.html`; frontend code communicates with the `/activities` API.
- Activity data is intentionally in memory and resets when the process restarts. Do not add persistence or change the data model unless the task requires it.
- Preserve existing route paths, HTTP status codes, error messages, redirects, and JSON response shapes unless the task explicitly changes the API contract.
- Keep route handlers straightforward and keep frontend changes within the existing static file layout.

## Development Commands
- Install dependencies: `pip install -r requirements.txt`
- Start the development server: `uvicorn src.app:app --reload`
- Run the test suite: `pytest -q`
- API documentation is available at `/docs` and `/redoc` while the server is running.

## Coding Standards

- Use four-space indentation, `snake_case` for functions and variables, and `PascalCase` for classes.
- Add type annotations to new public functions, route parameters, return values, and non-obvious data structures. Match nearby code when extending existing untyped code.
- Use FastAPI and `HTTPException` for request handling and API errors.
- Use the standard-library `logging` module for diagnostic messages when logging is needed. Do not use `print` for application diagnostics, and do not log secrets or sensitive request data.
- Use clear, descriptive names; do not use one-letter variable names except for conventional short-lived indices.
- Prefer small, focused changes that preserve existing public routes and response shapes.
- Do not introduce a formatter, linter, or type checker without a task-specific reason and corresponding configuration.

## Frontend Standards

- Use the existing vanilla JavaScript, DOM APIs, and `async`/`await` patterns.
- Keep frontend behavior compatible with the API routes in `src/app.py`.
- URL-encode activity names and email addresses when placing them in route paths.
- Preserve the existing static file layout and avoid adding a frontend framework for small UI changes.
- Treat activity and participant values as untrusted data when rendering them in the DOM.

## Security Rules

- Validate activity names, email addresses, and other client-provided values at the API boundary; do not rely only on HTML validation.
- URL-encode activity names and email addresses when placing them in route paths.
- Render API data with safe DOM APIs such as `textContent` where possible. Avoid injecting untrusted values with `innerHTML`.
- Never commit credentials, tokens, private keys, or other secrets. Read runtime secrets from environment variables or the deployment secret store.
- Do not expose internal exception details, filesystem paths, or sensitive request data in API responses or logs.
- Preserve FastAPI's validation and error handling instead of bypassing it with ad hoc parsing.

## Testing Expectations

- Add or update focused pytest tests for backend behavior changes in `tests/test_app.py`.
- Use `fastapi.testclient.TestClient` and pytest fixtures consistently with the existing tests.
- Follow Arrange/Act/Assert structure where it improves readability.
- Tests that mutate the shared `activities` dictionary must leave it restored for subsequent tests.
- Cover successful behavior, validation failures, missing resources, duplicate signups, and other relevant error paths for changed routes.
- Keep tests deterministic and independent; do not depend on test execution order or external services.
- Run `pytest -q` before completing backend changes.

## Change Discipline

- Inspect nearby code and existing tests before editing.
- Keep changes scoped to the requested behavior; avoid unrelated refactors.
- Preserve existing API status codes, error messages, redirects, and JSON response shapes unless the task explicitly changes the contract.
- Update documentation when commands, routes, or user-visible behavior change.
