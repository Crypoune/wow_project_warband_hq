-- Warband HQ - PostgreSQL database setup
-- Creates the application database and its dedicated user.
--
-- IMPORTANT:
-- Replace CHANGE_ME with a secure password before executing.
-- Do not commit a real password to Git.

CREATE USER warband_hq_user WITH PASSWORD 'CHANGE_ME';

CREATE DATABASE warband_hq

GRANT CONNECT ON DATABASE warband_hq TO warband_hq_user;

\connect warband_hq

GRANT USAGE ON SCHEMA public TO warband_hq_user;
