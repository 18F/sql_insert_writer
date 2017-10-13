-- This artificial example prepends the table name on many columns,
-- which is actually not generally done, but it's nice to demo
-- this package with

DROP TABLE IF EXISTS pet;
DROP TABLE IF EXISTS animal;
DROP TABLE IF EXISTS species;
DROP TABLE IF EXISTS habitat;

CREATE TABLE habitat (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

INSERT INTO habitat (
  name
)
VALUES
(
  'taiga'  -- ==> name
),
(
  'freshwater lakes'  -- ==> name
),
(
  'old barns'  -- ==> name
);


CREATE TABLE species (
    species_id SERIAL PRIMARY KEY,
    name TEXT,
    habitat_id INTEGER REFERENCES habitat(id)
);

INSERT INTO species (
  name,
  habitat_id
)
VALUES
(
  'caribou',  -- ==> name
  1  -- ==> habitat_id
),
(
  'barn owl',  -- ==> name
  3  -- ==> habitat_id
),
(
  'common loon',  -- ==> name
  2  -- ==> habitat_id
),
(
  'mosquito',  -- ==> name
  1  -- ==> habitat_id
),
(
  'walleye pike',  -- ==> name
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