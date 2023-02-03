#!/usr/bin/env python3
import os, click
COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()

if os.path.exists('.env'):
    print('Importing environment from .env...')
    for line in open('.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1]

from app import create_app
from app.models import db
#from flask_migrate import Migrate
#from celery import Celery

app = create_app()
#manager = Manager(app)
#migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    return dict(app=app, db=db)

@app.cli.command()
@click.option('--coverage/--no-coverage', default=False, help='Enable code coverage')
def test(coverage=False):
    """Run the unit tests."""
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import sys
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()

@app.cli.command()
@click.option('--length', default=25, help='Profile stack length')
@click.option('--profile-dir', default=None, help='Profile directory')
def profile(length, profile_dir):
    """Start the application under the code profiler."""
    from werkzeug.middleware.profiler import ProfilerMiddleware
    #from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length],
                                      profile_dir=profile_dir)
    app.run()

@app.cli.command()
def celery_run():
	os.exec('celery worker -A celery_runner -l info')
	#def make_celery(app):
	#	celery = Celery(app.import_name,
	#				backend=app.config['CELERY_RESULT_BACKEND'],
	#				broker=app.config['CELERY_BROKER_URL'])
	#	celery.conf.update(app.config)

	#	class ContextTask(celery.Task):
	#		def __call__(self, *args, **kwargs):
	#			with app.app_context():
	#				return self.run(*args, **kwargs)

	#	celery.Task = ContextTask
	#	return celery
	#celery = make_celery(app)

@app.cli.command()
def deploy():
    """Run deployment tasks."""
    #from flask_migrate import upgrade
    #from app.models import Role, Member

    # migrate database to latest revision
    #upgrade()

    # create user roles
    #Role.insert_roles()

    # create self-follows for all users
    #Member.add_self_follows()
