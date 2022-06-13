DROP TABLE IF EXISTS schedule CASCADE;
DROP TABLE IF EXISTS reviews CASCADE;
DROP VIEW IF EXISTS tutors CASCADE;
DROP TABLE IF EXISTS tutor_has_subjects CASCADE;
DROP VIEW IF EXISTS students CASCADE;
DROP TABLE IF EXISTS tutors_info CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS roles CASCADE;
DROP TABLE IF EXISTS subjects CASCADE;
DROP TABLE IF EXISTS days CASCADE;

CREATE TABLE IF NOT EXISTS roles(
    id SERIAL PRIMARY KEY,
    name varchar(30) NOT NULL UNIQUE
);
INSERT INTO roles(name) VALUES ('Student'), ('Tutor');

CREATE TABLE IF NOT EXISTS users(
    id SERIAL PRIMARY KEY,
    role INT REFERENCES roles(id),
    signup_date TIMESTAMP NOT NULL,
    email VARCHAR(320) NOT NULL UNIQUE,
    password VARCHAR(30) NOT NULL,
    first_name VARCHAR(30) NOT NULL,
    last_name VARCHAR(30) NOT NULL,
    phone VARCHAR(30) NOT NULL,
    telegram VARCHAR(30),
    about TEXT,
    education TEXT,
    year_born INTEGER NOT NULL,
    key CHAR(64) NOT NULL UNIQUE,
    key_created TIMESTAMP NOT NULL
);

CREATE TABLE tutors_info(
    tutor_id INTEGER PRIMARY KEY REFERENCES users(id),
    price INTEGER NOT NULL,
    experience INTEGER NOT NULL
);

CREATE VIEW students AS
SELECT * FROM users WHERE role=(SELECT id FROM roles WHERE name='student');

CREATE TABLE subjects(
    id SERIAL PRIMARY KEY,
    name varchar(30) NOT NULL UNIQUE
);
INSERT INTO subjects(name) VALUES
('Math'),
('English Language'),
('Biology'),
('Ukrainian Language'),
('Ukrainian Literature'),
('History'),
('Chemistry'),
('Georaphy'),
('Physics')
;

CREATE TABLE tutor_has_subjects(
    tutor_id INTEGER REFERENCES users(id),
    subject_id INTEGER REFERENCES subjects(id),
    PRIMARY KEY(tutor_id, subject_id)
);

CREATE TABLE reviews(
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES users(id),
    tutor_id INTEGER REFERENCES users(id),
    text TEXT,
    rating INTEGER NOT NULL,
    date TIMESTAMP NOT NULL
);

CREATE VIEW tutors AS
SELECT
    u.*,
    t.price,
    t.experience,
    ARRAY(SELECT ths.subject_id FROM tutor_has_subjects ths WHERE ths.tutor_id = u.id) "subjects",
    COALESCE((SELECT COUNT(r.*) FROM reviews r WHERE r.tutor_id = u.id), 0) "nb_reviews",
    COALESCE((SELECT AVG(r.rating) FROM reviews r WHERE r.tutor_id = u.id), 0) "rating"
FROM users u
INNER JOIN
    tutors_info t ON t.tutor_id = u.id;

CREATE TABLE days(
    id SERIAL PRIMARY KEY,
    name varchar(3) UNIQUE
);
INSERT INTO days(name) VALUES ('Mon'),  ('Tue'), ('Wed'), ('Thu'), ('Fri'), ('Sat'), ('Sun');

CREATE TABLE schedule(
    id SERIAL PRIMARY KEY,
    tutor_id INTEGER REFERENCES users(id),
    day INT REFERENCES days(id),
    hour INT NOT NULL
);
