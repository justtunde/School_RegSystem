-- ============================================
-- Student Course Registration System
-- Database Schema
-- ============================================

CREATE DATABASE StudentRegistrationDB;
USE StudentRegistrationDB;

-- ---------- Departments ----------
CREATE TABLE Departments (
    department_id   INT AUTO_INCREMENT PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL UNIQUE
);

-- ---------- Students ----------
CREATE TABLE Students (
    student_id     INT AUTO_INCREMENT PRIMARY KEY,
    first_name     VARCHAR(50) NOT NULL,
    last_name      VARCHAR(50) NOT NULL,
    email          VARCHAR(100) UNIQUE,
    department_id  INT,
    date_enrolled  DATE DEFAULT (CURRENT_DATE),
    FOREIGN KEY (department_id) REFERENCES Departments(department_id)
        ON DELETE SET NULL
);

-- ---------- Lecturers ----------
CREATE TABLE Lecturers (
    lecturer_id    INT AUTO_INCREMENT PRIMARY KEY,
    first_name     VARCHAR(50) NOT NULL,
    last_name      VARCHAR(50) NOT NULL,
    email          VARCHAR(100) UNIQUE,
    department_id  INT,
    FOREIGN KEY (department_id) REFERENCES Departments(department_id)
        ON DELETE SET NULL
);

-- ---------- Courses ----------
CREATE TABLE Courses (
    course_id     INT AUTO_INCREMENT PRIMARY KEY,
    course_code   VARCHAR(20) NOT NULL UNIQUE,
    course_name   VARCHAR(100) NOT NULL,
    credit_units  INT NOT NULL DEFAULT 3,
    department_id INT,
    lecturer_id   INT,
    FOREIGN KEY (department_id) REFERENCES Departments(department_id)
        ON DELETE SET NULL,
    FOREIGN KEY (lecturer_id) REFERENCES Lecturers(lecturer_id)
        ON DELETE SET NULL
);

-- ---------- Registrations (junction table) ----------
CREATE TABLE Registrations (
    registration_id  INT AUTO_INCREMENT PRIMARY KEY,
    student_id       INT NOT NULL,
    course_id        INT NOT NULL,
    date_registered  DATE DEFAULT (CURRENT_DATE),
    FOREIGN KEY (student_id) REFERENCES Students(student_id)
        ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES Courses(course_id)
        ON DELETE CASCADE,
    UNIQUE KEY unique_registration (student_id, course_id)
);

-- ---------- Indexes ----------
CREATE INDEX idx_student_lastname ON Students(last_name);
CREATE INDEX idx_course_code ON Courses(course_code);

-- ---------- View: Students with their departments ----------
CREATE OR REPLACE VIEW StudentsWithDepartments AS
SELECT s.student_id, s.first_name, s.last_name, s.email,
       d.department_name
FROM Students s
LEFT JOIN Departments d ON s.department_id = d.department_id;

-- ---------- View: Students registered per course ----------
CREATE OR REPLACE VIEW CourseRegistrationReport AS
SELECT c.course_code, c.course_name,
       s.student_id, s.first_name, s.last_name
FROM Registrations r
JOIN Courses c ON r.course_id = c.course_id
JOIN Students s ON r.student_id = s.student_id;

-- ---------- Stored Procedure: register a student for a course ----------
DELIMITER //
CREATE PROCEDURE RegisterStudent(
    IN p_student_id INT,
    IN p_course_id INT
)
BEGIN
    INSERT INTO Registrations (student_id, course_id)
    VALUES (p_student_id, p_course_id);
END //
DELIMITER ;

-- ---------- Stored Procedure: get all courses for a lecturer ----------
DELIMITER //
CREATE PROCEDURE CoursesByLecturer(
    IN p_lecturer_id INT
)
BEGIN
    SELECT course_code, course_name
    FROM Courses
    WHERE lecturer_id = p_lecturer_id;
END //
DELIMITER ;

select * from courses