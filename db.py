"""
Database connection and initialization for Knowledge Repository
PostgreSQL using psycopg2
"""

import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from config import config

# Connection pool
_pool = None


def get_pool():
    """Get or create the connection pool."""
    global _pool
    if _pool is None:
        db_url = config.DATABASE_URL
        if db_url:
            masked_url = db_url.split('@')[0].rsplit(':', 1)[0] + ':****@' + db_url.split('@')[1] if '@' in db_url else db_url
            print(f'Attempting database connection to: {masked_url}')
        else:
            print('DATABASE_URL environment variable is MISSING')
            
        _pool = pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=10,
            dsn=db_url
        )
        print('✅ Database connection pool created')
    return _pool


def query(sql, params=None):
    """Execute a query and return results."""
    conn = None
    try:
        conn = get_pool().getconn()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            
            # Check if this is a SELECT or RETURNING query
            if cur.description:
                rows = cur.fetchall()
                conn.commit()
                return {'rows': rows, 'rowcount': cur.rowcount}
            else:
                conn.commit()
                return {'rows': [], 'rowcount': cur.rowcount}
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            get_pool().putconn(conn)


def init_database():
    """Initialize database tables."""
    conn = None
    try:
        conn = get_pool().getconn()
        with conn.cursor() as cur:
            print('Initializing database...')
            
            # Categories table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    created_by TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Departments table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS departments (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    created_by TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Priorities table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS priorities (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    level INTEGER DEFAULT 0,
                    color TEXT,
                    created_by TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tags table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS tags (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    created_by TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Articles table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS articles (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    summary TEXT,
                    content TEXT,
                    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
                    department_id INTEGER REFERENCES departments(id) ON DELETE SET NULL,
                    priority_id INTEGER REFERENCES priorities(id) ON DELETE SET NULL,
                    author TEXT,
                    author_id TEXT,
                    views INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Article-Tags junction table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS article_tags (
                    article_id INTEGER NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
                    tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
                    PRIMARY KEY (article_id, tag_id)
                )
            """)
            
            # Attachments table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS attachments (
                    id SERIAL PRIMARY KEY,
                    article_id INTEGER REFERENCES articles(id) ON DELETE SET NULL,
                    file_name TEXT NOT NULL,
                    mime_type TEXT,
                    size INTEGER,
                    url TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Users table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    role TEXT DEFAULT 'user',
                    approved BOOLEAN DEFAULT false,
                    is_root BOOLEAN DEFAULT false,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login_at TIMESTAMP
                )
            """)
            
            # User favorites table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS user_favorites (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    article_id INTEGER NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, article_id)
                )
            """)
            
            # Recently viewed table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS recently_viewed (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    article_id INTEGER NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
                    viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, article_id)
                )
            """)
            
            # Create indexes
            cur.execute("CREATE INDEX IF NOT EXISTS idx_articles_category ON articles(category_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_articles_department ON articles(department_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_articles_priority ON articles(priority_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_articles_created ON articles(created_at)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_articles_title ON articles(title)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_attachments_article ON attachments(article_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_user_favorites_user ON user_favorites(user_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_user_favorites_article ON user_favorites(article_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_recently_viewed_user ON recently_viewed(user_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_recently_viewed_viewed_at ON recently_viewed(viewed_at)")
            
            conn.commit()
            print('Database initialized successfully')
            
    except Exception as e:
        if conn:
            conn.rollback()
        print(f'Error initializing database: {e}')
        raise e
    finally:
        if conn:
            get_pool().putconn(conn)


def seed_default_data():
    """Seed default categories, departments, and priorities."""
    conn = None
    try:
        conn = get_pool().getconn()
        with conn.cursor() as cur:
            # Default categories
            categories = [
                ('הדרכה', 'מאמרי הדרכה והכשרה'),
                ('נהלים', 'נהלי עבודה ותקנון'),
                ('טכני', 'מידע טכני ותמיכה'),
                ('שירות לקוחות', 'מידע לנציגי שירות'),
                ('מכירות', 'חומרי מכירות ומידע מסחרי'),
                ('כללי', 'מידע כללי')
            ]
            for name, desc in categories:
                cur.execute(
                    "INSERT INTO categories (name, description) VALUES (%s, %s) ON CONFLICT (name) DO NOTHING",
                    (name, desc)
                )
            
            # Default departments
            departments = [
                ('תפעול', 'מחלקת תפעול'),
                ('פיתוח', 'מחלקת פיתוח תוכנה'),
                ('שיווק', 'מחלקת שיווק ופרסום'),
                ('משאבי אנוש', 'מחלקת משאבי אנוש'),
                ('הנהלה', 'הנהלת החברה'),
                ('תמיכה טכנית', 'מחלקת תמיכה טכנית')
            ]
            for name, desc in departments:
                cur.execute(
                    "INSERT INTO departments (name, description) VALUES (%s, %s) ON CONFLICT (name) DO NOTHING",
                    (name, desc)
                )
            
            # Default priorities
            priorities = [
                ('דחוף', 4, '#DC3545'),
                ('גבוהה', 3, '#E74C5C'),
                ('בינונית', 2, '#FFC107'),
                ('נמוכה', 1, '#28A745')
            ]
            for name, level, color in priorities:
                cur.execute(
                    "INSERT INTO priorities (name, level, color) VALUES (%s, %s, %s) ON CONFLICT (name) DO NOTHING",
                    (name, level, color)
                )
            
            conn.commit()
            print('Default data seeded successfully')
            
    except Exception as e:
        if conn:
            conn.rollback()
        print(f'Error seeding data: {e}')
    finally:
        if conn:
            get_pool().putconn(conn)
