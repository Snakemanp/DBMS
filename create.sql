CREATE TABLE CITIZENS (
    CitizenID INT PRIMARY KEY,
    FullName VARCHAR(255) NOT NULL,
    DateOfBirth DATE NOT NULL,
    Gender VARCHAR(10) CHECK (Gender IN ('Male', 'Female', 'Other')),
    HouseholdID INT,
    ContactNumber VARCHAR(15),
    Job VARCHAR(50) ,   
    EducationalQualification VARCHAR(50) CHECK (EducationalQualification IN ('10th', '12th', 'Graduate', 'Post Graduate', 'Diploma', 'PhD', 'Other')),
    FatherID INT NULL,
    MotherID INT NULL,
    FOREIGN KEY (FatherID) REFERENCES CITIZENS(CitizenID) ON DELETE SET NULL,
    FOREIGN KEY (MotherID) REFERENCES CITIZENS(CitizenID) ON DELETE SET NULL
);

CREATE TABLE EMPLOYEE (
    EmployeeID INT PRIMARY KEY,
    CitizenID INT UNIQUE,
    Role VARCHAR(50) CHECK (Role IN ('Admin', 'Employee', 'Monitor')),
    FOREIGN KEY (CitizenID) REFERENCES CITIZENS(CitizenID) ON DELETE CASCADE
);

CREATE TABLE USERS(
    UserID INT PRIMARY KEY,
    Username VARCHAR(100) UNIQUE NOT NULL,
    Password VARCHAR(255) NOT NULL,
    Role VARCHAR(50) CHECK (Role IN ('Admin', 'Employee', 'Citizen', 'Monitor')),
    CitizenID INT,
    FOREIGN KEY (CitizenID) REFERENCES CITIZENS(CitizenID) ON DELETE SET NULL
);
