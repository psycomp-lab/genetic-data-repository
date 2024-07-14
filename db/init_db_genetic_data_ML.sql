-- This script was generated by the ERD tool in pgAdmin 4.
-- Please log an issue at https://redmine.postgresql.org/projects/pgadmin4/issues/new if you find any bugs, including reproduction steps.
BEGIN;

CREATE TABLE measurement_type(
    measurement_id INT GENERATED BY DEFAULT AS IDENTITY,
    name VARCHAR(64) NOT NULL,
    unit VARCHAR(15),
    PRIMARY KEY(measurement_id),
    CONSTRAINT uc_measurement_type UNIQUE (name, unit)
    );

ALTER TABLE measurement_type ALTER COLUMN measurement_id RESTART WITH 1;

CREATE TABLE sample_type(
    sample_id INT GENERATED BY DEFAULT AS IDENTITY,
    analysis_id VARCHAR(255) UNIQUE NOT NULL,
    PRIMARY KEY(sample_id)
    );

ALTER TABLE sample_type ALTER COLUMN sample_id RESTART WITH 1;

CREATE TABLE measurement(
    sample_id INT NOT NULL,
    measurement_id INT NOT NULL,
    value VARCHAR(15) NOT NULL,
    CONSTRAINT pk_measurement PRIMARY KEY(sample_id, measurement_id),
    CONSTRAINT fk_sampleid
        FOREIGN KEY(sample_id)
        REFERENCES sample_type(sample_id),
    CONSTRAINT fk_measurementid
        FOREIGN KEY(measurement_id) 
        REFERENCES measurement_type(measurement_id)
);


END;