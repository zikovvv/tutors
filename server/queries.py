create_db = """
CREATE DATABASE tutors
"""

get_all_users = """
SELECT * FROM users;
"""

set_user_key = """
UPDATE tutors SET key={} WHERE user_id={}
"""
