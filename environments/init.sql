-- Create the user with permissions to create databases
CREATE USER todo_user WITH PASSWORD 'todo_password' CREATEDB;
-- Create the database
CREATE DATABASE todo_db OWNER user;