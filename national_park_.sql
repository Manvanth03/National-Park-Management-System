CREATE TABLE Park (
    park_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(100) NOT NULL,
    established_year INT NOT NULL,
    visitor_count INT DEFAULT 0
);

CREATE TABLE Animals (
    animal_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    species VARCHAR(50) NOT NULL,
    park_id VARCHAR(20),
    FOREIGN KEY (park_id) REFERENCES Park(park_id)
);

CREATE TABLE Visitors (
    visitor_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100),
    visit_date DATE,
    park_id VARCHAR(20),
    FOREIGN KEY (park_id) REFERENCES Park(park_id)
);

CREATE TABLE Staff (
    staff_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100),
    role VARCHAR(50),
    park_id VARCHAR(20),
    FOREIGN KEY (park_id) REFERENCES Park(park_id)
);

CREATE TABLE Conservation (
    conservation_id VARCHAR(20) PRIMARY KEY,
    program_name VARCHAR(100),
    start_date DATE,
    park_id VARCHAR(20),
    end_date DATE,
    FOREIGN KEY (park_id) REFERENCES Park(park_id)
);

CREATE TABLE Users (
    id INT AUTO_INCREMENT PRIMARY KEY, 
    username VARCHAR(50) NOT NULL,     
    password VARCHAR(255) NOT NULL,    
    email VARCHAR(100) NOT NULL,       
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
);





Trigger

DELIMITER //

CREATE TRIGGER update_visitor_count 
AFTER INSERT ON Visitors
FOR EACH ROW
BEGIN
    UPDATE Park 
    SET visitor_count = visitor_count + 1
    WHERE park_id = NEW.park_id;
END; //

DELIMITER ;


CREATE VIEW conservation_status_view AS
SELECT
    c.conservation_id,
    c.program_name,
    c.start_date,
    c.end_date,
    c.park_id,
    p.name AS park_name,
    p.location AS park_location,
    -- Logic to determine the program status
    CASE
        WHEN c.end_date < CURDATE() THEN 'Completed'
        WHEN c.start_date <= CURDATE() AND c.end_date >= CURDATE() THEN 'Ongoing'
        WHEN c.start_date > CURDATE() THEN 'Upcoming'
    END AS program_status
FROM
    Conservation c
JOIN
    Park p ON c.park_id = p.park_id;

DELIMITER $$

CREATE TRIGGER check_established_year_before_insert
BEFORE INSERT ON Park
FOR EACH ROW
BEGIN
    IF NEW.established_year > YEAR(CURDATE()) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Established year cannot be in the future';
    END IF;
END$$

CREATE TRIGGER check_established_year_before_update
BEFORE UPDATE ON Park
FOR EACH ROW
BEGIN
    IF NEW.established_year > YEAR(CURDATE()) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Established year cannot be in the future';
    END IF;
END$$

DELIMITER ;

	