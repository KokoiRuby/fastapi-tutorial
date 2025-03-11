ALTER USER 'test'@'%' IDENTIFIED WITH caching_sha2_password BY 'test';

CREATE DATABASE IF NOT EXISTS fastapi;

USE fastapi;

CREATE TABLE IF NOT EXISTS posts (
    -- Auto-incrementing primary key
    post_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    
    -- Foreign key to users table
    user_id INT UNSIGNED NOT NULL,
    
    -- Post title
    title VARCHAR(254) NOT NULL,
    
    -- Timestamps
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,                             -- Set when record is created
    updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, -- Auto-updates when record changes
    
    -- Indexes
    PRIMARY KEY (post_id),    -- Primary key for fast lookups
    KEY (user_id)             -- Index on user_id for faster joins/lookups
) 
ENGINE=InnoDB                 -- Transactional storage engine
DEFAULT CHARSET=utf8mb4       -- Unicode character set
AUTO_INCREMENT=1;             -- Start auto-increment from 1