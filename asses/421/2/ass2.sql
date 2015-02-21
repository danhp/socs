CREATE TABLE Department
    (did INTEGER NOT NULL,
    departmentName CHAR(30),
    doctorId INTEGER NOT NULL,
    numberOfBeds INTEGER NOT NULL,
    PRIMARY KEY (did),
    FOREIGN KEY (doctorId) REFERENCES Doctor);

CREATE TABLE Employee
    (eid INTEGER NOT NULL,
    did INTEGER NOT NULL,
    firstName CHAR(30),
    lastName CHAR(30),
    jotTitle CHAR(30),
    startDate DATE,
    lastDate DATE,
    gender CHAR(1),
    dateOfBirth DATE,
    phone CHAR(10),
    email CHAR(30),
    city CHAR(30),
    medicareNumber INTEGER,
    PRIMARY KEY (eid),
    FOREIGN KEY (did) REFERENCES Department(did));

CREATE TABLE Patients
    (medicareNumber INTEGER NOT NULL,
    firstName CHAR(30),
    lastName CHAR(30),
    gender CHAR(1),
    dateOfBirth DATE,
    phone CHAR(30),
    address CHAR(30),
    PRIMARY KEY (medicareNumber));

CREATE TABLE Admissions
    (date DATE,
    medicareNumber INTEGER NOT NULL,
    doctorId INTEGER NOT NULL,
    reasonForAdmission CHAR(50),
    dateAdmitted DATE
    dateDischarged DATE
    PRIMARY KEY (date, medicareNumber, doctorId),
    FOREIGN KEY (medicareNumber) REFERENCES Patients(medicareNumber),
    FOREIGN KEY (doctorId) REFERENCES Doctors(doctorId));

CREATE TABLE Visits
    (v_time TIME,
    v_date DATE,
    medicareNumber INTEGER NOT NULL,
    doctorId INTEGER NOT NULL,
    diagnosis CHAR(50),
    medicalReport CHAR(100),
    PRIMARY KEY (v_time, v_date, medicareNumber, doctorId),
    FOREIGN KEY (medicareNumber) REFERENCES Patients(medicareNumber),
    FOREIGN KEY (doctorId) REFERENCES Doctors(doctorId));

CREATE TABLE Doctors
    (eid INTEGER NOT NULL,
    doctorId INTEGER NOT NULL,
    specialty CHAR(40),
    visitFee INTEGER NO NULL,
    PRIMARY KEY (eid, doctorId),
    FOREIGN KEY (eid) REFERENCES Employee(eid));

CREATE TABLE Nurses
    (eid INTEGER NOT NULL,
    nurseId INTEGER NOT NULL,
    specialty CHAR(40),
    PRIMARY KEY (eid, nurseId),
    FOREIGN KEY (eid) REFERENCES Employee(eid));
