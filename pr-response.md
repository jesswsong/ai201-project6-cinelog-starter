# PR Response Doc — CineLog Watchlist Feature

## AI Usage
<!-- Fill in at the end — how you used AI tools during this project -->

## Comment 1 — Rename
**What I did:** Renamed `save_to_watchlist` → `add_to_watchlist`. To find every call site I didn't trust a single grep on the service file — I searched the whole tree with `grep -rn "save_to_watchlist" --include="*.py" .`, which surfaced the definition in `services/watchlist_service.py` plus both the import and the call in `routes/watchlist/watchlist.py`. I confirmed nothing under `tests/` referenced the old name.
**How I verified:** Re-ran the same grep after renaming to prove zero remaining hits, then ran the full suite (`pytest tests/ -v`) so imports resolve and no call site points at the old symbol. (Committed earlier: `refactor: update save_to_watchlist function to add_to_watchlist`.)

## Comment 2 — Deduplication
**What I did:** Followed `add_to_collection()` in `services/collection_service.py` as my model. That function checks the film exists (`db.session.get`, raising `FilmNotFoundError`), then queries for an existing entry by `user_id`/`film_id` and raises `AlreadyInCollectionError` before creating a row. I mirrored this in `add_to_watchlist()`: added an `AlreadyInWatchlistError` class, inserted the guard `WatchlistEntry.query.filter_by(user_id=user_id, film_id=film_id).first()` between the film lookup and entry creation, and updated the docstring. Checking call sites, the route (`routes/watchlist/watchlist.py`) called the service with no `try/except`, so the new exception would surface as a 500 — I wrapped the call and mapped `FilmNotFoundError → 404`, `AlreadyInWatchlistError → 409`, matching the status codes in `routes/collection.py`.
**How I verified:** The collection suite proves the pattern via `test_add_to_collection_duplicate_raises` (adds twice, asserts the second raises and exactly one row exists). The watchlist service now uses the same `filter_by(...).first()` guard before insert, so identical behavior holds. Ran the full suite with `pytest tests/ -v`.

## Comment 3 — Missing test
**What I did:** Created `tests/test_watchlist.py`. My model was `test_add_to_collection_nonexistent_film_raises` in `tests/test_collection.py`. I copied its fixtures verbatim — `app` (in-memory SQLite with `db.create_all()`/`drop_all()`), `sample_user`, and `sample_film` — so the file is self-contained and matches codebase conventions. The equivalent test, `test_add_to_watchlist_nonexistent_film_raises`, passes the same all-zeros UUID sentinel and asserts `add_to_watchlist()` raises `FilmNotFoundError` (imported from `services.collection_service`, where the watchlist service re-uses it).
**How I verified:** `pytest tests/test_watchlist.py -v`, then the full suite `pytest tests/ -v`.

## Comment 4 — Default visibility
**My position:**
**Reasoning:**
**Tradeoff acknowledged:**

## Comment 5 — Sort order
**My position:**
**Reasoning:**
**Engagement with reviewer's point:**

## Comment 6 — Rebase
**What conflicted:**
**How I resolved it:**
**How I verified no conflict remains:**

## PR Description
<!-- Written at the end — feature overview, design decisions, manual testing steps -->