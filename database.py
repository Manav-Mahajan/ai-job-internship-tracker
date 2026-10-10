import sqlite3
import pandas as pd
from datetime import datetime
import os

DB_PATH = 'tracker.db'

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            title TEXT NOT NULL,
            type TEXT,
            description TEXT,
            applied_date TEXT,
            deadline TEXT,
            status TEXT,
            location TEXT,
            work_arrangement TEXT,
            url TEXT,
            salary TEXT,
            required_skills TEXT,
            notes TEXT,
            created_at TEXT
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS interviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            application_id INTEGER,
            interview_date TEXT,
            round TEXT,
            meeting_link TEXT,
            interviewer TEXT,
            notes TEXT,
            FOREIGN KEY(application_id) REFERENCES applications(id) ON DELETE CASCADE
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            priority TEXT,
            target_date TEXT,
            status TEXT
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            filepath TEXT NOT NULL,
            uploaded_at TEXT,
            application_id INTEGER,
            FOREIGN KEY(application_id) REFERENCES applications(id) ON DELETE SET NULL
        )
    ''')
    
    conn.commit()
    conn.close()

def add_application(data):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO applications (
            company, title, type, description, applied_date, deadline, status, 
            location, work_arrangement, url, salary, required_skills, notes, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['company'], data['title'], data['type'], data['description'],
        data['applied_date'], data['deadline'], data['status'], data['location'],
        data['work_arrangement'], data['url'], data['salary'], data['required_skills'],
        data['notes'], datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()

def update_application_status(app_id, status):
    conn = get_connection()
    c = conn.cursor()
    c.execute('UPDATE applications SET status = ? WHERE id = ?', (status, app_id))
    conn.commit()
    conn.close()

def update_application(app_id, data):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        UPDATE applications SET
            company = ?, title = ?, type = ?, description = ?, applied_date = ?, 
            deadline = ?, status = ?, location = ?, work_arrangement = ?, url = ?, 
            salary = ?, required_skills = ?, notes = ?
        WHERE id = ?
    ''', (
        data['company'], data['title'], data['type'], data['description'],
        data['applied_date'], data['deadline'], data['status'], data['location'],
        data['work_arrangement'], data['url'], data['salary'], data['required_skills'],
        data['notes'], app_id
    ))
    conn.commit()
    conn.close()

def delete_application(app_id):
    conn = get_connection()
    conn.execute("PRAGMA foreign_keys = ON")
    c = conn.cursor()
    c.execute('DELETE FROM applications WHERE id = ?', (app_id,))
    conn.commit()
    conn.close()

def get_all_applications():
    conn = get_connection()
    df = pd.read_sql_query('SELECT * FROM applications', conn)
    conn.close()
    return df

def add_interview(data):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO interviews (
            application_id, interview_date, round, meeting_link, interviewer, notes
        ) VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        data['application_id'], data['interview_date'], data['round'],
        data['meeting_link'], data['interviewer'], data['notes']
    ))
    conn.commit()
    conn.close()

def get_interviews():
    conn = get_connection()
    query = '''
        SELECT i.*, a.company, a.title 
        FROM interviews i
        JOIN applications a ON i.application_id = a.id
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def delete_interview(int_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM interviews WHERE id = ?', (int_id,))
    conn.commit()
    conn.close()

def add_skill(data):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO skills (name, category, priority, target_date, status)
        VALUES (?, ?, ?, ?, ?)
    ''', (data['name'], data['category'], data['priority'], data['target_date'], data['status']))
    conn.commit()
    conn.close()

def update_skill_status(skill_id, status):
    conn = get_connection()
    c = conn.cursor()
    c.execute('UPDATE skills SET status = ? WHERE id = ?', (status, skill_id))
    conn.commit()
    conn.close()

def delete_skill(skill_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM skills WHERE id = ?', (skill_id,))
    conn.commit()
    conn.close()

def get_skills():
    conn = get_connection()
    df = pd.read_sql_query('SELECT * FROM skills', conn)
    conn.close()
    return df

def add_resume(filename, filepath, application_id=None):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO resumes (filename, filepath, uploaded_at, application_id)
        VALUES (?, ?, ?, ?)
    ''', (filename, filepath, datetime.now().isoformat(), application_id))
    conn.commit()
    conn.close()

def get_resumes():
    conn = get_connection()
    df = pd.read_sql_query('SELECT * FROM resumes', conn)
    conn.close()
    return df

def delete_resume(resume_id, filepath):
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
        except:
            pass
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM resumes WHERE id = ?', (resume_id,))
    conn.commit()
    conn.close()
