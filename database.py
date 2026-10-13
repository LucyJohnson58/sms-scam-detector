import sqlite3
from pathlib import Path
from datetime import datetime

# ---------------------------------------------------------------
# ABSOLUTE PATHS — works no matter where you launch python from
# ---------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "scans.db"


def init_db():
    """Create the database and tables if they don't exist."""
    (BASE_DIR / "data").mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    # Table 1: Every scan performed
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT NOT NULL,
            prediction INTEGER NOT NULL,        -- 1 = fraud, 0 = normal
            confidence REAL NOT NULL,           -- 0.0 to 1.0
            source TEXT DEFAULT 'terminal',     -- 'terminal' or 'web'
            created_at TEXT NOT NULL
        )
    ''')

    # Table 2: User reports on scans (feedback)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_id INTEGER NOT NULL,
            user_feedback TEXT NOT NULL,        -- 'correct' or 'wrong'
            comment TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (scan_id) REFERENCES scans(id)
        )
    ''')

    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")


def save_scan(message, prediction, confidence, source='terminal'):
    """Insert a new scan and return its ID."""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO scans (message, prediction, confidence, source, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (message, prediction, confidence, source, datetime.now().isoformat()))

    scan_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return scan_id


def save_report(scan_id, user_feedback, comment=''):
    """Insert user feedback for a scan."""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO reports (scan_id, user_feedback, comment, created_at)
        VALUES (?, ?, ?, ?)
    ''', (scan_id, user_feedback, comment, datetime.now().isoformat()))

    conn.commit()
    conn.close()


def get_recent_scans(limit=10):
    """Fetch the most recent scans."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, message, prediction, confidence, source, created_at
        FROM scans
        ORDER BY id DESC
        LIMIT ?
    ''', (limit,))

    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_stats():
    """Return summary statistics."""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM scans')
    total = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM scans WHERE prediction = 1')
    fraud_count = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM scans WHERE prediction = 0')
    normal_count = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM reports')
    reports_count = cursor.fetchone()[0]

    conn.close()
    return {
        'total_scans': total,
        'fraud_count': fraud_count,
        'normal_count': normal_count,
        'reports_count': reports_count,
    }


if __name__ == '__main__':
    # If you run this file directly, it will initialize the DB and print stats
    init_db()
    stats = get_stats()
    print("\nCurrent stats:")
    for key, value in stats.items():
        print(f"  {key}: {value}")