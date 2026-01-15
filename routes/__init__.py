"""
Routes package for Knowledge Repository Flask Backend
"""

from routes.auth import auth_bp
from routes.categories import categories_bp
from routes.departments import departments_bp
from routes.priorities import priorities_bp
from routes.tags import tags_bp
from routes.articles import articles_bp
from routes.attachments import attachments_bp
from routes.users import users_bp
from routes.favorites import favorites_bp
from routes.recently_viewed import recently_viewed_bp


def register_blueprints(app):
    """Register all blueprints with the Flask app."""
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(categories_bp, url_prefix='/api/categories')
    app.register_blueprint(departments_bp, url_prefix='/api/departments')
    app.register_blueprint(priorities_bp, url_prefix='/api/priorities')
    app.register_blueprint(tags_bp, url_prefix='/api/tags')
    app.register_blueprint(articles_bp, url_prefix='/api/articles')
    app.register_blueprint(attachments_bp, url_prefix='/api')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(favorites_bp, url_prefix='/api/favorites')
    app.register_blueprint(recently_viewed_bp, url_prefix='/api/recently-viewed')
