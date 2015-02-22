CREATE TABLE Departments
    (did INTEGER NOT NULL UNIQUE,
    departmentName CHAR(30) NOT NULL,
    doctorId INTEGER,
    numberOfBeds INTEGER NOT NULL,
    PRIMARY KEY (did));

CREATE TABLE Employees
    (eid INTEGER NOT NULL UNIQUE,
    did INTEGER NOT NULL,
    firstName CHAR(20),
    lastName CHAR(20),
    jotTitle CHAR(20),
    startDate DATE,
    lastDate DATE,
    gender CHAR(1),
    dateOfBirth DATE,
    phone CHAR(10),
    email CHAR(20),
    address CHAR(20),
    city CHAR(20),
    medicareNumber INTEGER UNIQUE,
    PRIMARY KEY (eid),
    FOREIGN KEY (did) REFERENCES Departments(did));

CREATE TABLE Patients
    (medicareNumber INTEGER NOT NULL UNIQUE,
    firstName CHAR(15),
    lastName CHAR(15),
    gender CHAR(1),
    dateOfBirth DATE,
    phone CHAR(10),
    address CHAR(20),
    PRIMARY KEY (medicareNumber));

CREATE TABLE Doctors
    (eid INTEGER NOT NULL UNIQUE,
    doctorId INTEGER NOT NULL UNIQUE,
    specialty CHAR(15),
    visitFee INTEGER NOT NULL,
    PRIMARY KEY (eid, doctorId),
    FOREIGN KEY (eid) REFERENCES Employees(eid));

CREATE TABLE Nurses
    (eid INTEGER NOT NULL UNIQUE,
    nurseId INTEGER NOT NULL UNIQUE,
    specialty CHAR(15),
    PRIMARY KEY (eid, nurseId),
    FOREIGN KEY (eid) REFERENCES Employees(eid));

CREATE TABLE Admissions
    (dateAdmitted DATE NOT NULL,
    medicareNumber INTEGER NOT NULL,
    doctorId INTEGER NOT NULL,
    reasonForAdmission CHAR(20),
    dateDischarged DATE,
    PRIMARY KEY (dateAdmitted, medicareNumber, doctorId),
    FOREIGN KEY (doctorId) REFERENCES Doctors(doctorId),
    FOREIGN KEY (medicareNumber) REFERENCES Patients(medicareNumber));

CREATE TABLE Visits
    (v_time TIME NOT NULL,
    v_date DATE NOT NULL,
    medicareNumber INTEGER NOT NULL,
    doctorId INTEGER NOT NULL,
    diagnosis CHAR(15),
    medicalReport CHAR(30),
    PRIMARY KEY (v_time, v_date, medicareNumber, doctorId),
    FOREIGN KEY (doctorId) REFERENCES Doctors(doctorId),
    FOREIGN KEY (medicareNumber) REFERENCES Patients(medicareNumber));


INSERT INTO Departments VALUES(1, 'Emergencies', 4, 50);
INSERT INTO Departments VALUES(2, 'Cardiology', 2, 20);
INSERT INTO Departments VALUES(3, 'Neurology', 1, 5);
INSERT INTO Departments VALUES(4, 'Oncology', 6, 12);

INSERT INTO Employees VALUES(1, 3, 'Akira', 'Kurosawa', 'Doctor', '1954-04-26', '1990-01-01', 'M', NULL, '5550001111', NULL, NULL, 'Montreal', 100);
INSERT INTO Employees VALUES(2, 2, 'Ridley', 'Scott', 'Doctor', '2012-06-08', NULL, 'M', NULL, '5550002222', NULL, NULL, 'Montreal', 101);
INSERT INTO Employees VALUES(3, 2, 'Nicolas', 'Refn', 'Doctor', '2011-09-16', NULL, 'M', NULL, '5550003333', NULL, NULL, 'Montreal', 102);
INSERT INTO Employees VALUES(4, 1, 'David', 'Fincher', 'Doctor', '1995-05-22', NULL, 'M', NULL, '5550004444', NULL, NULL, 'Montreal', 103);
INSERT INTO Employees VALUES(5, 3, 'Stanley', 'Kubrick', 'Doctor', '1980-05-23', NULL, 'M', NULL, '5550005555', NULL, NULL, 'Montreal', 104);
INSERT INTO Employees VALUES(6, 4, 'Quentin', 'Tarentino', 'Doctor', '1994-09-10', NULL, 'M', NULL, '5550006666', NULL, NULL, 'Montreal', 105);

INSERT INTO Doctors VALUES(1, 10, 'Neurology', 50);
INSERT INTO Doctors VALUES(2, 11, 'Heart', 30);
INSERT INTO Doctors VALUES(3, 12, 'Heart', 30);
INSERT INTO Doctors VALUES(4, 13, 'ER', 70);
INSERT INTO Doctors VALUES(5, 14, 'Neurology', 50);
INSERT INTO Doctors VALUES(6, 15, 'Cancer', 100);

INSERT INTO Employees VALUES(7, 4, 'Carey', 'Mulligan', 'Nurse', '2011-09-16', NULL, 'F', NULL, '5551111111', NULL, NULL, 'Laval', 106);
INSERT INTO Employees VALUES(8, 1, 'Sigourney', 'Weaver', 'Nurse', '1979-05-29', NULL, 'F', NULL, '5551112222', NULL, NULL, 'Montreal', 107);
INSERT INTO Employees VALUES(9, 2, 'Brie', 'Larson', 'Nurse', '2013-08-23', NULL, 'F', NULL, '5551113333', NULL, NULL, 'Laval', 108);
INSERT INTO Employees VALUES(10, 1, 'Christina', 'Hendricks', 'Nurse', '2011-09-16', NULL, 'F', NULL, '5551114444', NULL, NULL, 'Montreal', 109);
INSERT INTO Employees VALUES(11, 3, 'Sean', 'Young', 'Nurse', '1982-06-25', NULL, 'F', NULL, '5551115555', NULL, NULL, 'Montreal', 110);
INSERT INTO Employees VALUES(12, 2, 'Mary', 'Winstead', 'Nurse', '2010-08-11', NULL, 'F', NULL, '5551116666', NULL, NULL, 'Montreal', 111);

INSERT INTO Nurses VALUES(7, 10, 'Cancer');
INSERT INTO Nurses VALUES(8, 11, 'ER');
INSERT INTO Nurses VALUES(9, 12, 'Heart');
INSERT INTO Nurses VALUES(10, 13, 'ER');
INSERT INTO Nurses VALUES(11, 14, 'Neurology');
INSERT INTO Nurses VALUES(12, 15, 'Heart');

INSERT INTO Employees VALUES(13, 1, 'Morgan', 'Freeman', 'Janitor', '1995-05-22', NULL, NULL, NULL, '5552221111', NULL, NULL, 'Montreal', 112);
INSERT INTO Employees VALUES(14, 1, 'Harrison', 'Ford', 'Janitor', '1982-06-25', NULL, NULL, NULL, '5552222222', NULL, NULL, 'Montreal', 113);
INSERT INTO Employees VALUES(15, 1, 'Rutger', 'Haeur', 'Janitor', '1982-06-25', NULL, NULL, NULL, '5552223333', NULL, NULL, 'Montreal', 114);
INSERT INTO Employees VALUES(16, 1, 'Ryan', 'Gosling', 'Janitor', '2011-09-16', NULL, NULL, NULL, '5552224444', NULL, NULL, 'Montreal', 115);
INSERT INTO Employees VALUES(17, 1, 'Samuel', 'Jackson', 'Janitor', '1994-09-10', NULL, NULL, NULL, '5552225555', NULL, NULL, 'Montreal', 116);
INSERT INTO Employees VALUES(18, 1, 'John', 'Travolta', 'Janitor', '1994-09-10', NULL, NULL, NULL, '5552226666', NULL, NULL, 'Montreal', 117);
INSERT INTO Employees VALUES(19, 1, 'Vithaya', 'Pansringarm', 'Janitor', '2013-05-22', NULL, NULL, NULL, '5552227777', NULL, NULL, 'Montreal', 118);
INSERT INTO Employees VALUES(20, 1, 'Micheal', 'Cera', 'Janitor', '2010-08-11', NULL, NULL, NULL, '5552228888', NULL, NULL, 'Montreal', 119);

INSERT INTO Patients VALUES(100, 'Akira', 'Kurosawa', 'M', '1930-01-01', '5550001111', NULL);
INSERT INTO Patients VALUES(101, 'Ridley', 'Scott', 'M', '1960-01-01', '5550002222', NULL);
INSERT INTO Patients VALUES(104, 'Stanley', 'Kubrick', 'M', '1960-01-01', '5550002222', NULL);
INSERT INTO Patients VALUES(106, 'Carey', 'Mulligan', 'F', '1985-01-01', '5551111111', NULL);
INSERT INTO Patients VALUES(108, 'Brie', 'Larson', 'F', '1988-01-01', '5551113333', NULL);
INSERT INTO Patients VALUES(111, 'Mary', 'Windstead', 'F', '1987-01-01', '5551116666', NULL);
INSERT INTO Patients VALUES(110, 'Sean', 'Young', 'F', '1970-01-01', '5551115555', NULL);
INSERT INTO Patients VALUES(113, 'Harrison', 'Ford', 'M', '1940-01-01', '5552222222', NULL);
INSERT INTO Patients VALUES(114, 'Rutger', 'Haeur', 'M', '1942-01-01', '5552223333', NULL);
INSERT INTO Patients VALUES(116, 'Samuel', 'Jackson', 'M', '1943-01-01', '5552225555', NULL);
INSERT INTO Patients VALUES(119, 'Micheal', 'Cera', 'M', '1983-01-01', '5552228888', NULL);

INSERT INTO Patients VALUES(200, 'John', 'Doe', 'M', '2000-01-01', 5553330000, NULL);
INSERT INTO Patients VALUES(201, 'John', 'Doe', 'M', '2000-01-01', 5553331111, NULL);
INSERT INTO Patients VALUES(202, 'John', 'Doe', 'M', '2000-01-01', 5553332222, NULL);
INSERT INTO Patients VALUES(203, 'John', 'Doe', 'M', '2000-01-01', 5553333333, NULL);
INSERT INTO Patients VALUES(204, 'John', 'Doe', 'M', '2000-01-01', 5553334444, NULL);
INSERT INTO Patients VALUES(205, 'John', 'Doe', 'M', '2000-01-01', 5553335555, NULL);
INSERT INTO Patients VALUES(206, 'John', 'Doe', 'M', '2000-01-01', 5553336666, NULL);
INSERT INTO Patients VALUES(207, 'John', 'Doe', 'M', '2000-01-01', 5553337777, NULL);
INSERT INTO Patients VALUES(208, 'John', 'Doe', 'M', '2000-01-01', 5553338888, NULL);
INSERT INTO Patients VALUES(209, 'John', 'Doe', 'M', '2000-01-01', 5553339999, NULL);

INSERT INTO Admissions VALUES('2014-11-03', 101, 12, 'Heart', '2014-11-11');
INSERT INTO Admissions VALUES('2014-11-21', 101, 12, 'Heart', '2014-12-01');
INSERT INTO Admissions VALUES('2013-09-04', 101, 12, 'Cancer', '2013-09-05');
INSERT INTO Admissions VALUES('2013-08-01', 101, 12, 'Heart', '2013-09-01');
INSERT INTO Admissions VALUES('2013-07-01', 101, 12, 'Cancer', '2013-07-02');
INSERT INTO Admissions VALUES('2013-07-01', 200, 13, 'HIV', '2013-07-02');
INSERT INTO Admissions VALUES('2013-02-01', 200, 13, 'Cancer', '2013-02-02');
INSERT INTO Admissions VALUES('2013-02-01', 201, 13, 'HIV', '2013-02-02');
INSERT INTO Admissions VALUES('2013-02-03', 201, 11, 'Heart', '2013-02-06');
INSERT INTO Admissions VALUES('2013-03-06', 201, 11, 'Heart', '2013-03-07');
INSERT INTO Admissions VALUES('2014-03-06', 119, 11, 'HIV', '2014-03-07');
INSERT INTO Admissions VALUES('2014-03-05', 116, 11, 'HIV', '2014-03-08');
INSERT INTO Admissions VALUES('2014-03-05', 111, 11, 'HIV', '2014-03-06');
INSERT INTO Admissions VALUES('2014-03-05', 110, 10, 'HIV', '2014-03-06');
INSERT INTO Admissions VALUES('2014-03-05', 110, 14, 'HIV', '2014-03-06');
INSERT INTO Admissions VALUES('2014-03-05', 110, 13, 'Pregnancy', '2014-03-09');
INSERT INTO Admissions VALUES('2014-02-03', 111, 13, 'Pregnancy', '2014-02-11');
INSERT INTO Admissions VALUES('2011-01-05', 108, 13, 'Pregnancy', '2011-01-10');
INSERT INTO Admissions VALUES('2014-09-05', 207, 13, 'Heart', '2014-09-10');
INSERT INTO Admissions VALUES('2010-03-05', 209, 13, 'Heart', '2010-03-09');

INSERT INTO Visits VALUES('14:00:00', '2013-01-11', 111, 11, 'Healthy', 'All is good');
INSERT INTO Visits VALUES('14:20:00', '2013-01-11', 113, 11, 'Healthy', 'All is good');
INSERT INTO Visits VALUES('14:40:00', '2013-01-11', 119, 11, 'Healthy', 'All is good');
INSERT INTO Visits VALUES('15:00:00', '2013-01-11', 116, 11, 'Healthy', 'All is good');
INSERT INTO Visits VALUES('15:20:00', '2013-01-11', 200, 11, 'Cancer', 'X-ray not good');

INSERT INTO Visits VALUES('11:00:00', '2011-02-28', 108, 10, 'Healthy', 'All is good');
INSERT INTO Visits VALUES('11:00:00', '2011-02-10', 108, 11, 'Healthy', 'All is good');
INSERT INTO Visits VALUES('11:00:00', '2011-02-12', 108, 12, 'Healthy', 'All is good');
INSERT INTO Visits VALUES('11:00:00', '2011-02-20', 108, 13, 'Healthy', 'All is good');
INSERT INTO Visits VALUES('11:00:00', '2011-02-11', 108, 14, 'Healthy', 'All is good');

SELECT * FROM Departments;
SELECT * FROM Employees;
SELECT * FROM Patients;
SELECT * FROM Doctors;
SELECT * FROM Nurses;
SELECT * FROM Admissions;
SELECT * FROM Visits;

-- DELETE FROM Employees cascade;
-- DELETE FROM Patients cascade;
-- DELETE FROM Doctors cascade;
-- DELETE FROM Nurses cascade;
-- DELETE FROM Admissions cascade;
-- DELETE FROM Visits cascade;
-- DELETE FROM Departments cascade;

DROP TABLE Departments, Employees, Patients, Admissions, Visits, Doctors, Nurses;
