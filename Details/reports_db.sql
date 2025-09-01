-- =============================================
-- Database: reports_db
-- =============================================
DROP DATABASE IF EXISTS reports_db;
CREATE DATABASE reports_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE reports_db;

SET FOREIGN_KEY_CHECKS = 0;

-- =============================================
-- INSTITUTIONS
-- =============================================
CREATE TABLE institutions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    address VARCHAR(255),
    contact_email VARCHAR(150),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- USERS
-- =============================================
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    institution_id INT,
    id_number VARCHAR(100) NOT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'student', 'lecturer') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_user_institution FOREIGN KEY (institution_id) REFERENCES institutions(id) ON DELETE SET NULL
);

-- =============================================
-- STUDENTS
-- =============================================
CREATE TABLE students (
    id INT PRIMARY KEY,
    admission_number VARCHAR(50) UNIQUE NOT NULL,
    course VARCHAR(100),
    year_of_study INT CHECK (year_of_study >= 1),
    department VARCHAR(100),
    CONSTRAINT fk_student_user FOREIGN KEY (id) REFERENCES users(id) ON DELETE CASCADE
);

-- =============================================
-- LECTURERS
-- =============================================
CREATE TABLE lecturers (
    id INT PRIMARY KEY,
    staff_number VARCHAR(50) UNIQUE NOT NULL,
    department VARCHAR(100),
    specialization VARCHAR(150),
    CONSTRAINT fk_lecturer_user FOREIGN KEY (id) REFERENCES users(id) ON DELETE CASCADE
);

-- =============================================
-- LAB TEMPLATES
-- =============================================
CREATE TABLE lab_templates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    lecturer_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    description VARCHAR(500),
    fields JSON NOT NULL, -- structure of report
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_template_lecturer FOREIGN KEY (lecturer_id) REFERENCES lecturers(id) ON DELETE CASCADE
);

-- =============================================
-- SUBMISSIONS
-- =============================================
CREATE TABLE submissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    template_id INT NOT NULL,
    submission_values JSON NOT NULL,
    grade DECIMAL(5,2),
    feedback TEXT,
    status ENUM('graded', 'pending', 'disputed') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_submission_student FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    CONSTRAINT fk_submission_template FOREIGN KEY (template_id) REFERENCES lab_templates(id) ON DELETE CASCADE
);

-- =============================================
-- DISPUTES
-- =============================================
CREATE TABLE disputes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    submission_id INT NOT NULL,
    student_id INT NOT NULL,
    lecturer_id INT NOT NULL,
    reason TEXT NOT NULL,
    resolution TEXT,
    status ENUM('open', 'resolved', 'rejected') DEFAULT 'open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_dispute_submission FOREIGN KEY (submission_id) REFERENCES submissions(id) ON DELETE CASCADE,
    CONSTRAINT fk_dispute_student FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    CONSTRAINT fk_dispute_lecturer FOREIGN KEY (lecturer_id) REFERENCES lecturers(id) ON DELETE CASCADE
);

-- =============================================
-- ATTACHMENTS
-- =============================================
CREATE TABLE attachments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    submission_id INT NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_attachment_submission FOREIGN KEY (submission_id) REFERENCES submissions(id) ON DELETE CASCADE
);

-- =============================================
-- AUDIT LOGS
-- =============================================
CREATE TABLE audit_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    action VARCHAR(200) NOT NULL,
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_audit_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- =============================================
-- ANALYTICS
-- =============================================
CREATE TABLE analytics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    template_id INT NOT NULL UNIQUE,
    avg_score DECIMAL(5,2),
    submission_count INT,
    failed_count INT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_analytics_template FOREIGN KEY (template_id) REFERENCES lab_templates(id) ON DELETE CASCADE
);

-- =============================================
-- VIEWS
-- =============================================
CREATE VIEW disputed_reports AS
SELECT
    d.id AS dispute_id,
    d.created_at AS dispute_created,
    s.id AS submission_id,
    lt.title AS template_title,
    u_student.name AS student_name,
    u_lecturer.name AS lecturer_name,
    d.reason,
    d.status
FROM disputes d
JOIN submissions s ON d.submission_id = s.id
JOIN lab_templates lt ON s.template_id = lt.id
JOIN users u_student ON s.student_id = u_student.id
JOIN users u_lecturer ON d.lecturer_id = u_lecturer.id;

-- =============================================
-- TRIGGERS
-- =============================================
DELIMITER $$

CREATE TRIGGER update_analytics_after_grade
AFTER UPDATE ON submissions
FOR EACH ROW
BEGIN
    IF NEW.grade IS NOT NULL THEN
        INSERT INTO analytics (template_id, avg_score, submission_count, failed_count)
        VALUES (
            NEW.template_id,
            (SELECT AVG(grade) FROM submissions WHERE template_id = NEW.template_id),
            (SELECT COUNT(*) FROM submissions WHERE template_id = NEW.template_id),
            (SELECT COUNT(*) FROM submissions WHERE template_id = NEW.template_id AND grade < 50)
        )
        ON DUPLICATE KEY UPDATE
            avg_score = VALUES(avg_score),
            submission_count = VALUES(submission_count),
            failed_count = VALUES(failed_count),
            updated_at = CURRENT_TIMESTAMP;
    END IF;
END$$

DELIMITER ;

SET FOREIGN_KEY_CHECKS = 1;