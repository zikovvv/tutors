CREATE TABLE IF NOT EXISTS tutors_have_students(
    tutor_id INTEGER REFERENCES users(id),
    student_id INTEGER REFERENCES users(id),
    accepted_by_student BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY(tutor_id, student_id)
);

CREATE TABLE schedule(
    id SERIAL PRIMARY KEY,
    tutor_id INTEGER REFERENCES users(id),
    day INT NOT NULL,
    hour INT NOT NULL
);