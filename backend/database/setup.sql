-- Warband HQ - MySQL database setup
-- Creates the application and test databases and a dedicated database user.
--
-- IMPORTANT:
-- Replace CHANGE_ME with a secure password before executing.
-- Do not commit a real password to Git.

CREATE DATABASE IF NOT EXISTS warband_hq
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

CREATE DATABASE IF NOT EXISTS warband_hq_test
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'warband_hq_user'@'127.0.0.1'
    IDENTIFIED BY 'CHANGE_ME';

GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, INDEX, DROP, REFERENCES
    ON warband_hq.* TO 'warband_hq_user'@'127.0.0.1';

GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, INDEX, DROP, REFERENCES
    ON warband_hq_test.* TO 'warband_hq_user'@'127.0.0.1';
