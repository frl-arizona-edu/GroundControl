
CREATE USER auvsi_owner WITH PASSWORD 'auvsi';

CREATE TYPE status_type AS ENUM ('unprocessed', 'processing', 'positive', 'negative');

CREATE TABLE images(name        TEXT NOT NULL PRIMARY KEY,
                    center      POINT NOT NULL,
                    status      status_type DEFAULT 'unprocessed',
                    sentTime    NUMERIC DEFAULT NULL,
                    recvTime    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    procTime    NUMERIC DEFAULT NULL,
                    priority    INTEGER NOT NULL DEFAULT 100);

GRANT ALL ON images TO auvsi_owner;
