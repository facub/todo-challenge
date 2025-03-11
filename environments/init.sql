-- Create the user if it does not exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'todo_user') THEN
        CREATE ROLE todo_user WITH LOGIN PASSWORD 'todo_password';
    END IF;
END $$;

-- Create the database if it does not exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'todo_db') THEN
        CREATE DATABASE todo_db OWNER todo_user;
    END IF;
END $$;

-- Grant all privileges on the database to the user
GRANT ALL PRIVILEGES ON DATABASE todo_db TO todo_user;
