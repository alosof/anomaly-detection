CREATE SCHEMA alerts;

CREATE TABLE alerts.cpu
(
    id       serial,
    time     timestamp,
    expected float,
    actual   float,
    diff     float
);

CREATE TABLE alerts.cpu_temp
(
    id       serial,
    time     timestamp,
    expected float,
    actual   float,
    diff     float
);

CREATE TABLE alerts.ram
(
    id       serial,
    time     timestamp,
    expected float,
    actual   float,
    diff     float
);

CREATE TABLE alerts.swap
(
    id       serial,
    time     timestamp,
    expected float,
    actual   float,
    diff     float
);

CREATE TABLE alerts.disk
(
    id       serial,
    time     timestamp,
    expected float,
    actual   float,
    diff     float
);
