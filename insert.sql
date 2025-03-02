-- Inserting parents
INSERT INTO CITIZENS (CitizenID, FullName, DateOfBirth, Gender, ContactNumber, EducationalQualification, Job, HouseholdID) VALUES
(1, 'Ramesh Sharma', '1965-03-10', 'Male', '9876500001', 'Graduate', 'Teacher', 201),
(2, 'Sunita Sharma', '1970-07-15', 'Female', '9876500002', 'Post Graduate', 'Doctor', 201),
(3, 'Mahesh Verma', '1968-12-20', 'Male', '9876500003', '12th', 'Farmer', 202),
(4, 'Anita Verma', '1975-06-05', 'Female', '9876500004', 'Graduate', 'Housewife', 202);

-- Inserting children with parent references
INSERT INTO CITIZENS (CitizenID, FullName, DateOfBirth, Gender, ContactNumber, EducationalQualification, Job, HouseholdID, FatherID, MotherID) VALUES
(5, 'Amit Sharma', '1990-05-12', 'Male', '9876543210', 'Post Graduate', 'Software Engineer', 201, 1, 2),
(6, 'Priya Verma', '1995-08-25', 'Female', '9867543211', 'Graduate', 'Bank Manager', 202, 3, 4),
(7, 'Rajesh Kumar', '1988-02-17', 'Male', '9856543222', '12th', 'Electrician', 203, NULL, NULL),
(8, 'Sanya Mehta', '2000-11-05', 'Female', '9846543233', 'PhD', 'Professor', 204, NULL, NULL);


INSERT INTO EMPLOYEE (EmployeeID, CitizenID, Role) VALUES
(101, 5, 'Sarpanch'),         
(102, 6, 'Secretary'),        
(103, 7, 'Surveyor'),        
(104, 8, 'Health Officer'); 

INSERT INTO USERS (UserID, Username, Password, Role, CitizenID) VALUES
(101, 'ramesh_sharma', 'fatherpass1', 'Citizen', 1),
(102, 'sunita_sharma', 'motherpass1', 'Citizen', 2),
(103, 'mahesh_verma', 'fatherpass2', 'Citizen', 3),
(104, 'anita_verma', 'motherpass2', 'Citizen', 4),
(201, 'amit_admin', 'password123', 'Employee', 5),
(202, 'priya_emp', 'emp456', 'Employee', 6),
(203, 'rajesh_mon', 'mon789', 'Employee', 7),
(204, 'sanya_citizen', 'citizen101', 'Employee', 8);

INSERT INTO ASSETS (AssetID, Type, Location, InstallationDate, Condition, LastMaintenanceDate) VALUES
(1, 'Water Pump', 'Village A', '2018-06-15', 'Good', '2023-07-10'),
(2, 'Solar Street Light', 'Village B', '2020-02-20', 'Needs Repair', '2023-10-05'),
(3, 'Public Library', 'Village C', '2015-09-12', 'Good', '2022-12-01'),
(4, 'Community Hall', 'Village D', '2017-11-25', 'Damaged', NULL);

INSERT INTO HOUSEHOLDS (HouseholdID, Address, Income, NumberOfMembers, PropertyValue) VALUES
(201, 'Village A, House 1', 50000, 4, 300000),
(202, 'Village B, House 2', 70000, 5, 400000),
(203, 'Village C, House 3', 30000, 3, 250000),
(204, 'Village D, House 4', 60000, 6, 350000);


