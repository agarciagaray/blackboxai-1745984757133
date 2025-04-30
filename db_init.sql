CREATE DATABASE IF NOT EXISTS credit_scoring_db;
USE credit_scoring_db;

CREATE TABLE customer (
    id INT AUTO_INCREMENT PRIMARY KEY,
    document_type VARCHAR(10) NOT NULL,
    document_number VARCHAR(50) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    birth_date DATE NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(100),
    UNIQUE KEY unique_document (document_type, document_number)
);

CREATE TABLE credit_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    experian_score FLOAT,
    transunion_score FLOAT,
    active_obligations INT,
    total_debt FLOAT,
    payment_history TEXT,
    recent_inquiries INT,
    FOREIGN KEY (customer_id) REFERENCES customer(id) ON DELETE CASCADE
);

CREATE TABLE socioeconomic_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    monthly_income FLOAT,
    occupation VARCHAR(100),
    economic_sector VARCHAR(100),
    employment_duration_years INT,
    education_level VARCHAR(100),
    marital_status VARCHAR(50),
    dependents INT,
    housing_type VARCHAR(100),
    FOREIGN KEY (customer_id) REFERENCES customer(id) ON DELETE CASCADE
);

CREATE TABLE credit_request (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    amount_requested FLOAT NOT NULL,
    term_months INT NOT NULL,
    interest_rate FLOAT NOT NULL,
    credit_purpose VARCHAR(255),
    collateral VARCHAR(255),
    request_date DATETIME NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customer(id) ON DELETE CASCADE
);

CREATE TABLE credit_evaluation (
    id INT AUTO_INCREMENT PRIMARY KEY,
    credit_request_id INT NOT NULL,
    decision VARCHAR(50) NOT NULL,
    score FLOAT NOT NULL,
    population_percentile FLOAT,
    decision_factors TEXT,
    max_recommended_amount FLOAT,
    recommended_term_months INT,
    evaluation_date DATETIME NOT NULL,
    model_version VARCHAR(20) NOT NULL,
    FOREIGN KEY (credit_request_id) REFERENCES credit_request(id) ON DELETE CASCADE
);
