DROP TABLE IF EXISTS atm_temperat;

DROP TABLE IF EXISTS atm_pressure;

DROP TABLE IF EXISTS weather;

CREATE TABLE atm_temperat(
    [sol] INTEGER PRIMARY KEY,
    [av] INTEGER,
    [mn] INTEGER,
    [mx] INTEGER
);

CREATE TABLE atm_pressure(
    [sol] INTEGER PRIMARY KEY,
    [av] INTEGER,
    [mn] INTEGER,
    [mx] INTEGER
);