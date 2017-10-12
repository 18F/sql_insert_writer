-- This artificial example prepends the table name on many columns,
-- which is actually not generally done, but it's nice to demo
-- this package with

DROP TABLE IF EXISTS animal;
DROP TABLE IF EXISTS species;
DROP TABLE IF EXISTS habitat;

CREATE TABLE habitat (
    habitat_id SERIAL PRIMARY KEY,
    habitat_name TEXT NOT NULL
);

INSERT INTO habitat (
  habitat_name
)
VALUES
(
  'taiga'  -- ==> habitat_name
),
(
  'freshwater lakes'  -- ==> habitat_name
),
(
  'old barns'  -- ==> habitat_name
);

CREATE TABLE species (
    species_id SERIAL PRIMARY KEY,
    species_name TEXT,
    habitat_id INTEGER REFERENCES habitat(habitat_id)
);

INSERT INTO species (
  species_name,
  habitat_id
)
VALUES
(
  'caribou',  -- ==> species_name
  1  -- ==> habitat_id
),
(
  'barn owl',  -- ==> species_name
  3  -- ==> habitat_id
),
(
  'common loon',  -- ==> species_name
  2  -- ==> habitat_id
),
(
  'mosquito',  -- ==> species_name
  1  -- ==> habitat_id
),
(
  'walleye pike',  -- ==> species_name
  2  -- ==> habitat_id
);

CREATE TABLE animal (
    id SERIAL PRIMARY KEY,
    kg NUMERIC,
    species_id INTEGER REFERENCES species(species_id)
);

INSERT INTO animal (
  kg,
  species_id
)
VALUES
(
  0.0001,  -- ==> kg
  4  -- ==> species_id
),
(
  2,  -- ==> kg
  5  -- ==> species_id
),
(
  1,  -- ==> kg
  3  -- ==> species_id
),
(
  300,  -- ==> kg
  1  -- ==> species_id
),
(
  380,  -- ==> kg
  1  -- ==> species_id
),
(
  1.2,  -- ==> kg
  3-- ==> species_id
),
(
  1.4,  -- ==> kg
  2  -- ==> species_id
);

CREATE TABLE pet (
    id SERIAL PRIMARY KEY,
    name TEXT,
    kg NUMERIC,
    species_name TEXT,
    habitat_name TEXT
);