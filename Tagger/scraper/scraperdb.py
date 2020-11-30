import sqlite3

def make_new_db(title):
    conn = sqlite3.connect(title)

    conn_cursor = conn.cursor()

    create_file = '''CREATE TABLE file(
                        id INTEGER PRIMARY KEY,
                        length INT,
                        title VARCHAR(255) NOT NULL UNIQUE,
                        link VARCHAR(255))'''

    create_tag = '''CREATE TABLE tag(
                        id INTEGER PRIMARY KEY,
                        name VARCHAR(255) NOT NULL UNIQUE)'''

    create_match = '''CREATE TABLE match(
                            id INTEGER PRIMARY KEY,
                            file_id INTEGER,
                            tag_id INTEGER,
                            FOREIGN KEY (file_id) REFERENCES file(id),
                            FOREIGN KEY (tag_id) REFERENCES tag(id))'''

    conn_cursor.execute(create_file)
    conn_cursor.execute(create_tag)
    conn_cursor.execute(create_match)

    conn.close()
