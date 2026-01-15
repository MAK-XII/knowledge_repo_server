"""
Knowledge Repository - Flask Backend Server
PostgreSQL Async Version (Python port of Express server)
"""

import os
import sys

# Add the server directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from config import config
from db import init_database, seed_default_data, get_pool
from routes import register_blueprints
from auth import admin_required

# Initialize Flask app
app = Flask(__name__, static_folder='..')
app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH

# Enable CORS
CORS(app)

# Register all API blueprints
register_blueprints(app)


# ==========================================
# Static File Serving
# ==========================================

@app.route('/')
@app.route('/index.html')
def serve_index():
    """Serve the main index.html."""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/login.html')
def serve_login():
    """Serve the login page."""
    return send_from_directory(app.static_folder, 'login.html')


@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    """Serve uploaded files."""
    return send_from_directory(config.UPLOAD_FOLDER, filename)


@app.route('/css/<path:filename>')
def serve_css(filename):
    """Serve CSS files."""
    return send_from_directory(os.path.join(app.static_folder, 'css'), filename)


@app.route('/js/<path:filename>')
def serve_js(filename):
    """Serve JavaScript files."""
    return send_from_directory(os.path.join(app.static_folder, 'js'), filename)


@app.route('/api-client.js')
def serve_api_client():
    """Serve the API client JavaScript."""
    return send_from_directory(app.static_folder, 'api-client.js')


@app.route('/favicon.ico')
def serve_favicon():
    """Serve favicon."""
    try:
        return send_from_directory(app.static_folder, 'favicon.ico')
    except:
        return '', 204


# ==========================================
# System Routes (Maintenance)
# ==========================================

@app.route('/api/admin/run-migration', methods=['GET'])
@admin_required
def run_migration():
    """Run database migrations (admin only)."""
    try:
        print('Running migration from web trigger...')
        from db import query
        
        # Add created_by columns if they don't exist
        query("ALTER TABLE tags ADD COLUMN IF NOT EXISTS created_by TEXT")
        query("ALTER TABLE categories ADD COLUMN IF NOT EXISTS created_by TEXT")
        query("ALTER TABLE departments ADD COLUMN IF NOT EXISTS created_by TEXT")
        query("ALTER TABLE priorities ADD COLUMN IF NOT EXISTS created_by TEXT")
        
        return jsonify({'success': True, 'message': 'Migration executed successfully'})
        
    except Exception as e:
        print(f'Migration error: {e}')
        return jsonify({'error': str(e)}), 500


# ==========================================
# Error Handlers
# ==========================================

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors - try to serve static files."""
    # Try to serve as a static file
    path = e.description if hasattr(e, 'description') else ''
    try:
        return send_from_directory(app.static_folder, path)
    except:
        return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500


# ==========================================
# Main Entry Point
# ==========================================

if __name__ == '__main__':
    # Ensure uploads directory exists
    os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)
    
    # Initialize database
    try:
        init_database()
        seed_default_data()
    except Exception as e:
        print(f'Failed to initialize database: {e}')
    
    # Print startup banner
    port = config.PORT
    print(f"""
╔════════════════════════════════════════════════════════╗
║                                                        ║
║   Knowledge Repository Server (Flask/Postgres)        ║
║                                                        ║
║   Server running at: http://localhost:{port}             ║
║   API available at:  http://localhost:{port}/api         ║
║                                                        ║
╚════════════════════════════════════════════════════════╝
    """)
    
    # Run the server
    app.run(
        host='0.0.0.0',
        port=port,
        debug=config.DEBUG
    )
