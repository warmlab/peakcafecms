import os

from flask import Flask
from flask import send_from_directory, url_for
from flask_migrate import Migrate

from config import config

from app.models import db

def create_app():
    app = Flask(__name__)
    config_name = os.getenv('FLASK_CONFIG') or 'default'
    print("[%s]" % config_name)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app);

    db.init_app(app)
    migrate = Migrate(app, db) # --
    # should be comment
    #init_admin(app)
    #mail.init_app(app)
    #celery = make_celery(app)

    if not app.debug and not app.testing and not app.config['SSL_DISABLE']:
        from flask_sslify import SSLify
        sslify = SSLify(app)

    from .home import home as home_blueprint
    app.register_blueprint(home_blueprint, url_prefix='/', name="home")

    #from .api import api as api_blueprint
    #app.register_blueprint(api_blueprint, url_prefix='/api')

    #from .admin import admin as admin_blueprint
    #app.register_blueprint(admin_blueprint, url_prefix='/admin')

    # just for develop
    @app.route('/media/<path:filename>', methods=['GET'])
    def media(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=False)

    # for favicon.ico
    @app.route('/favicon.ico', methods=['GET'])
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

    from flask import request
    @app.route('/robots.txt', methods=['GET', "POST"])
    def robots():
        print(request.headers)
        print(request.json)
        return send_from_directory(os.path.join(app.root_path, 'static'),
                               'robots.txt', mimetype='text/plain')

    return app
