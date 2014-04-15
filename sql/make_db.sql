
CREATE USER auvsi_owner WITH PASSWORD 'auvsi';

CREATE TYPE status_type AS ENUM ('unprocessed', 'processing', 'process_error', 'reprocess', 'ack');

CREATE TABLE images(name        TEXT NOT NULL PRIMARY KEY,
                    center      POINT NOT NULL,
                    recvTime    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    sentTime    NUMERIC DEFAULT -1,
                    status      status_type DEFAULT 'unprocessed',
                    priority    INTEGER NOT NULL DEFAULT 100);

CREATE TABLE cvresults(id       SERIAL PRIMARY KEY,
                       bounds   BOX NOT NULL,
                       results  TEXT NOT NULL);

CREATE TABLE images_cvresults(name      TEXT NOT NULL REFERENCES images(name),
                              result_id INT NOT NULL REFERENCES cvresults(id),
                              PRIMARY KEY (name, result_id));

GRANT ALL ON images TO auvsi_owner;
GRANT ALL ON cvresults TO auvsi_owner;
GRANT ALL ON images_cvresults TO auvsi_owner;
GRANT ALL ON SEQUENCE cvresults_id_seq TO auvsi_owner;
