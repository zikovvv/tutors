get_all_users = """
SELECT * FROM users;
"""

get_user_by_email = """
SELECT * FROM users WHERE email=%s;
"""

set_user_key = """
UPDATE users SET key=%s, key_created=CURRENT_TIMESTAMP WHERE user_id=%s;
"""

get_user_by_email_and_password = """
SELECT * FROM users WHERE email=%s AND password=%s;
"""

get_user_by_key = """
SELECT * FROM users WHERE key=%s
"""

add_user = """
INSERT INTO users(role, signup_date, email, password, first_name, last_name, phone, telegram, about, education, year_born, key, key_created)
VALUES (%s, CURRENT_TIMESTAMP, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP);
"""

add_tutor_info = """
INSERT INTO tutors_info VALUES (%s, %s, %s);
"""

get_tutors = """
SELECT u.*, t.*
FROM users u
INNER JOIN tutors_info t ON u.id = t.id
WHERE
t.price BETWEEN %f AND %f AND
EXISTS(SELECT * FROM tutor_has_subject ts WHERE ts.tutor_id = u.id AND ts.subject_id = )
;
"""

get_subjects = """
SELECT name FROM subjects ORDER BY id;
"""

get_roles = """
SELECT name FROM roles ORDER BY id;
"""

add_subject_to_tutor = """
INSERT INTO tutor_has_subjects VALUES (%s, %s)
"""
