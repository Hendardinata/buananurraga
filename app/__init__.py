from flask import Flask

def create_app(config_class='app.config.Config'):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions here (if any)
    from app.extensions import db
    db.init_app(app)

    # Register blueprints here
    from app.routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp)
    
    from app.routes.dashboard_routes import dashboard_bp
    app.register_blueprint(dashboard_bp)
    
    from app.routes.member_routes import member_bp
    app.register_blueprint(member_bp)
    
    from app.routes.staging_routes import staging_bp
    app.register_blueprint(staging_bp)
    
    from app.routes.promotion_routes import promotion_bp
    app.register_blueprint(promotion_bp)
    
    from app.routes.kta_routes import kta_bp
    app.register_blueprint(kta_bp)
    
    from app.routes.public_routes import public_bp
    app.register_blueprint(public_bp)
    
    from app.routes.whatsapp_routes import whatsapp_bp
    app.register_blueprint(whatsapp_bp)
    
    from app.routes.budget_routes import budget_bp
    app.register_blueprint(budget_bp)

    from app.routes.user_routes import user_bp
    app.register_blueprint(user_bp)

    from app.routes.achievement_routes import achievement_bp
    app.register_blueprint(achievement_bp)

    from flask import session, request, flash, redirect, url_for
    from datetime import datetime
    
    @app.before_request
    def check_session():
        # Allow static files, auth, and public routes to be accessed without active session
        if request.endpoint and (request.endpoint.startswith('static') or request.endpoint.startswith('auth.') or request.endpoint.startswith('public.')):
            return
            
        if 'user_id' in session:
            from app.models.user import User
            user = User.query.filter_by(username=session['user_id']).first()
            if not user:
                session.clear()
                return redirect(url_for('auth.login'))
                
            # Verify session token
            if session.get('session_token') != user.session_token:
                session.clear()
                flash('Sesi Anda telah berakhir karena login dari perangkat lain.', 'error')
                return redirect(url_for('auth.login'))
                
            # Update last_active
            user.last_active = datetime.utcnow()
            db.session.commit()

    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'version': app.config.get('TEMPLATE_VERSION')}

    return app
