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
**My position:** Keep the default at **`public=True`**. CineLog is a community film-tracking app, so the default should reinforce the product's core loop — discovering what others are watching.

**Reasoning:** Since CineLog's thesis is a community-based film tracking app, the center of the app is in connecting people. A public-by-default watchlist means every new user immediately contributes to shared feeds, "what people are watching" surfaces, and recommendation data — the features that make a *community* app worth using. 

**Tradeoff acknowledged:** The cost is privacy and least-astonishment — a user could add a film without realizing it's world-readable, and that exposure isn't retroactively undoable. I accept that risk because (a) a watchlist is low-sensitivity data (films you plan to watch, not private notes), and (b) the fix is UX, not a default flip: make visibility obvious at add-time and give a one-tap toggle to make any entry private. That preserves the community value while giving privacy-conscious users an easy, explicit escape hatch. If usage data later shows users are surprised or opting out in bulk, that's the signal to revisit — and this note documents that the `public=True` default is an intentional, community-driven choice, not an inherited accident.

## Comment 5 — Sort order
**My position:** I agree with sorting the watchlist by **date-added, newest first**, and make that the single sort order. I changed `get_watchlist()` from `Film.title.asc()` to `WatchlistEntry.date_added.desc()`. 

**Reasoning:** Date-added is the conventional default for "saved for later" lists (watchlists, playlists, reading lists) because recency tracks intent — the film you just added is usually the one you're actually thinking about watching next. It also makes the watchlist consistent with `get_collection()`, which already orders by `date_added.desc()`; two sibling features sorting differently would be a surprise for no good reason, and keeping them aligned means one mental model for the whole app. 

**Engagement with reviewer's point:** The maintainer's argument — "most users want to see what they added recently" — is correct, and it's the reason I'm adopting date-added rather than merely conceding it. They framed it as date-added *vs.* alphabetical, and I agree alphabetical is the weaker default: it's a *lookup* order (useful when you already know the title and want to find it), which is a search/filter problem, not a default-sort problem. Baking a rarely-needed lookup order in as an option would add API surface and an untested code path to dodge a decision the maintainer explicitly wanted made. So the decision, documented here per their request, is: date-added, newest first, full stop. If real usage later shows demand for alphabetical, we can add an explicit, tested `?sort=` param then — driven by evidence rather than speculation.

## Comment 6 — Rebase
**What conflicted:**
**How I resolved it:**
**How I verified no conflict remains:**

## PR Description
<!-- Written at the end — feature overview, design decisions, manual testing steps -->