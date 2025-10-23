CREATE DATABASE IF NOT EXISTS School;
USE School;

CREATE TABLE User (
    UserId INT PRIMARY KEY AUTO_INCREMENT,
    RoleName ENUM('Admin','Teacher','Student') Default 'Admin',
    Name VARCHAR(50) NOT NULL,
    Email VARCHAR(25) UNIQUE NOT NULL,
    Password VARCHAR(255) NOT NULL,
    Phone VARCHAR(10),
    IsActive ENUM('Active','Inactive') DEFAULT 'Active',
    Created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Track creation
    Updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE    CURRENT_TIMESTAMP
) AUTO_INCREMENT=1001;


CREATE TABLE Admin(
Adminid INT AUTO_INCREMENT PRIMARY KEY,
Userid INT,
institutionName VARCHAR(50),
Name VARCHAR(50),
Email VARCHAR(50),
Phone VARCHAR(20),
IsActive ENUM('Active','Inactive')DEFAULT 'Active',
FOREIGN KEY (Userid) REFERENCES user(Userid)ON DELETE CASCADE
)AUTO_INCREMENT=2001;



CREATE TABLE Teacher (
    TeacherId INT PRIMARY KEY AUTO_INCREMENT,
    UserId INT ,
    AdminId INT,    
    Name VARCHAR(50),
    EmailId VARCHAR(25),
    Password VARCHAR(25),
    PhoneNo VARCHAR(10),
    Subject VARCHAR(25),
    IsActive ENUM('Active','Inactive') DEFAULT 'Active',
    FOREIGN KEY (UserId) REFERENCES User(UserId) ON DELETE CASCADE,
    FOREIGN KEY (AdminId) REFERENCES Admin(AdminId) ON DELETE CASCADE
) AUTO_INCREMENT=3001;

CREATE TABLE Subject (
    SubjectId INT AUTO_INCREMENT PRIMARY KEY,
    TeacherID INT,
    SubjectName VARCHAR(50),
    IsActive ENUM('Active','Inactive') DEFAULT 'Active',
    FOREIGN KEY (TeacherID) REFERENCES Teacher(TeacherId) ON DELETE CASCADE
);


CREATE TABLE Student (
    StudentId INT PRIMARY KEY AUTO_INCREMENT,
    AdminId INT,
    UserId INT ,   
    Name VARCHAR(50),
    EmailId VARCHAR(25),
    Password VARCHAR(25),
    PhoneNo VARCHAR(10),
    IsActive ENUM('Active','Inactive') DEFAULT 'Active',
    Gender ENUM('Male','Female','Others'),
    DOB DATE,
    ClassName VARCHAR(50),
    Department VARCHAR(50),
    Subject VARCHAR(50),
    SubjectId INT,
    FatherName VARCHAR(50),
    MotherName VARCHAR(50),
    Address VARCHAR(30),
    FOREIGN KEY (UserId) REFERENCES User(UserId) ON DELETE CASCADE,
    FOREIGN KEY (AdminId) REFERENCES Admin(AdminId) ON DELETE CASCADE,
    FOREIGN KEY (SubjectId) REFERENCES Subject(SubjectId) ON DELETE CASCADE
) AUTO_INCREMENT=4001;


desc admin;
select * from teacher;
ALTER TABLE Teacher MODIFY COLUMN Password VARCHAR(255);
ALTER TABLE Student MODIFY COLUMN Password VARCHAR(255);

desc student;
select * from admin;

-- Modify both columns to VARCHAR(255)
ALTER TABLE subject drop COLUMN TeacherId;

ALTER TABLE student
CHANGE COLUMN SubjectId SubjectIds VARCHAR(255);

CREATE TABLE Attendance (
    AttendanceId INT AUTO_INCREMENT PRIMARY KEY,
    StudentID INT,
    SubjectId INT,
    Status ENUM('P', 'A') NOT NULL,
    Date DATE,
    FOREIGN KEY (StudentID) REFERENCES Student(StudentId) ON DELETE CASCADE,
    FOREIGN KEY (SubjectId) REFERENCES Subject(SubjectId) ON DELETE CASCADE,
    UNIQUE KEY unique_attendance (StudentID, SubjectId, Date)
);



CREATE TABLE StudentSubject (
    StudentId INT NOT NULL,
    SubjectId INT NOT NULL,
    PRIMARY KEY (StudentId, SubjectId),
    FOREIGN KEY (StudentId) REFERENCES student(StudentId) ON DELETE CASCADE,
    FOREIGN KEY (SubjectId) REFERENCES subject(SubjectId) ON DELETE CASCADE
);

ALTER TABLE student
ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;




