-- Create the user with permissions to create databases
CREATE USER test_user WITH PASSWORD 'test_password' CREATEDB;
-- Create the database
CREATE DATABASE test_todo_db OWNER test_user;