-- Create the user if it does not exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'local_todo_user') THEN
        CREATE ROLE local_todo_user WITH LOGIN PASSWORD 'local_todo_password';
    END IF;
END $$;

-- Create the database if it does not exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'local_todo_db') THEN
        CREATE DATABASE local_todo_db OWNER local_todo_user;
    END IF;
END $$;

-- Grant all privileges on the database to the user
GRANT ALL PRIVILEGES ON DATABASE local_todo_db TO local_todo_user;