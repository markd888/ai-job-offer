-- One row per install that opted in. No IP, no user agent, nothing personal.
CREATE TABLE IF NOT EXISTS installs (
  id            TEXT PRIMARY KEY,   -- random uuid4 generated on the user's machine
  first_version TEXT NOT NULL,
  first_seen    TEXT NOT NULL       -- YYYY-MM-DD (day only)
);
