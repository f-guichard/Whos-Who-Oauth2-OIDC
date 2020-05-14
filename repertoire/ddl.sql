CREATE TABLE utilisateurs (
  id TEXT PRIMARY KEY,
  nom TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  avatar TEXT NOT NULL
);
