from flask import Flask

def create_app(config_class='app.config.Config'):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions here (if any)

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

    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'version': app.config.get('TEMPLATE_VERSION')}

    return app
