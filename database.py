"""SQLite database for Shiny Pokemon Hunter app."""

import sqlite3
import os
from datetime import datetime
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'shiny_hunter.db')

def init_db():
    """Initialize the database with required tables."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Caught shinies table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS caught_shinies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pokemon_id INTEGER NOT NULL,
                pokemon_name TEXT NOT NULL,
                caught_date TEXT NOT NULL,
                hunt_method TEXT,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Hunt sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hunt_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pokemon_id INTEGER NOT NULL,
                pokemon_name TEXT NOT NULL,
                method TEXT NOT NULL,
                encounter_count INTEGER DEFAULT 0,
                start_time TEXT NOT NULL,
                end_time TEXT,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        # Hunt progress table (current hunts)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hunt_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pokemon_id INTEGER NOT NULL,
                pokemon_name TEXT NOT NULL,
                method TEXT NOT NULL,
                encounter_count INTEGER DEFAULT 0,
                time_spent_minutes REAL DEFAULT 0,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(pokemon_id, method)
            )
        ''')
        
        conn.commit()

@contextmanager
def get_db():
    """Get database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

# Shinies operations
def add_shiny(pokemon_id, pokemon_name, hunt_method=None, notes=None):
    """Record a caught shiny."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO caught_shinies (pokemon_id, pokemon_name, hunt_method, notes, caught_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (pokemon_id, pokemon_name, hunt_method, notes, datetime.now().strftime('%Y-%m-%d %H:%M')))
        conn.commit()
        return cursor.lastrowid

def get_all_shinies():
    """Get all caught shinies."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM caught_shinies ORDER BY caught_date DESC')
        return cursor.fetchall()

def get_shiny_count():
    """Get total shiny count."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM caught_shinies')
        return cursor.fetchone()['count']

# Hunt progress operations
def update_hunt_progress(pokemon_id, pokemon_name, method, encounters=1, time_spent=0):
    """Update hunt progress for a Pokemon."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO hunt_progress (pokemon_id, pokemon_name, method, encounter_count, time_spent_minutes, last_updated)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(pokemon_id, method) DO UPDATE SET
                encounter_count = encounter_count + excluded.encounter_count,
                time_spent_minutes = time_spent_minutes + excluded.time_spent_minutes,
                last_updated = CURRENT_TIMESTAMP
        ''', (pokemon_id, pokemon_name, method, encounters, time_spent))
        conn.commit()

def get_hunt_progress():
    """Get all hunt progress records."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM hunt_progress ORDER BY last_updated DESC')
        return cursor.fetchall()

def get_hunt_stats():
    """Get hunt statistics."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                SUM(encounter_count) as total_encounters,
                SUM(time_spent_minutes) as total_time,
                COUNT(*) as active_hunts
            FROM hunt_progress
        ''')
        return cursor.fetchone()

def reset_hunt(pokemon_id, method):
    """Reset hunt progress for a Pokemon."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM hunt_progress WHERE pokemon_id = ? AND method = ?', (pokemon_id, method))
        conn.commit()

def delete_shiny(shiny_id):
    """Delete a shiny record."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM caught_shinies WHERE id = ?', (shiny_id,))
        conn.commit()

if __name__ == '__main__':
    init_db()
    print("Database initialized!")