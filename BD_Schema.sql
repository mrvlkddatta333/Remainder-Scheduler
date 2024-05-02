-- Create the database
CREATE DATABASE IF NOT EXISTS scheduler_db;
USE scheduler_db;

-- Create the User table
CREATE TABLE IF NOT EXISTS User (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(64) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL
);

-- Create the Category table
CREATE TABLE IF NOT EXISTS Category (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(64) NOT NULL,
    user_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES User(id)
);

-- Create the Task table
CREATE TABLE IF NOT EXISTS Task (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(120) NOT NULL,
    description TEXT,
    due_date DATETIME NOT NULL,
    category_id INT NOT NULL,
    FOREIGN KEY (category_id) REFERENCES Category(id)
);

-- Create the Reminder table with CASCADE on deletion
CREATE TABLE IF NOT EXISTS Reminder (
    id INT AUTO_INCREMENT PRIMARY KEY,
    notification_method VARCHAR(64) NOT NULL,
    `interval` INT NOT NULL,
    sent_at DATETIME,
    task_id INT NOT NULL,
    FOREIGN KEY (task_id) REFERENCES Task(id) ON DELETE CASCADE
);

ALTER TABLE user
MODIFY COLUMN password_hash VARCHAR(255);

ALTER TABLE User
ADD COLUMN first_name VARCHAR(64) AFTER username,
ADD COLUMN last_name VARCHAR(64) AFTER first_name,
ADD COLUMN phone_number VARCHAR(20) AFTER last_name,
ADD COLUMN preferences TEXT AFTER phone_number;

ALTER TABLE Category
ADD COLUMN category_type VARCHAR(64) NOT NULL AFTER name;

ALTER TABLE Task
ADD COLUMN attachment VARCHAR(256) AFTER category_id;

ALTER TABLE user ADD UNIQUE INDEX ix_user_phone_number (phone_number);

-- Create the File table
CREATE TABLE IF NOT EXISTS File (
    id INT AUTO_INCREMENT PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    file_data LONGBLOB NOT NULL,
    file_type VARCHAR(255) NOT NULL,
    task_id INT NOT NULL,
    FOREIGN KEY (task_id) REFERENCES Task(id)
);

-- Add the reminder_datetime column to the Reminder table
ALTER TABLE Reminder ADD COLUMN reminder_datetime DATETIME NOT NULL;

-- Create an index on the reminder_datetime column for better performance
CREATE INDEX ix_reminder_reminder_datetime ON Reminder (reminder_datetime);

ALTER TABLE Reminder MODIFY COLUMN notification_method VARCHAR(64) DEFAULT 'email';

ALTER TABLE Reminder DROP COLUMN `interval`;