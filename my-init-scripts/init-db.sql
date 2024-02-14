-- Create a separate database for Airflow
CREATE ROLE airflow LOGIN PASSWORD 'airflow';
CREATE DATABASE airflow OWNER airflow;
GRANT ALL PRIVILEGES ON DATABASE airflow TO airflow;

-- Create another database for your application
CREATE DATABASE myapplication;
GRANT ALL PRIVILEGES ON DATABASE myapplication TO myuser;

