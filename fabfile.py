import os
import random
from datetime import datetime
from fabric.contrib.files import append, exists, sed
from fabric.api import cd, env, local, run

REPO_URL = ''
SERVER_PASSWORD = os.environ['SERVER_PASS']
SITE_FOLDER = ''
DB_NAME = ''


def get_timestamp():
    cur_time = datetime.now()
    return datetime.strftime(cur_time, "%Y-%m-%d-%H-%M")


def _get_database_backups():
    # i would like to get a copy of databases before updating
    run('mkdir -p {SITE_FOLDER}/{subfolder}'.format(
        SITE_FOLDER=SITE_FOLDER, subfolder='db-backups'
    ))

    db_name_no_ext = DB_NAME[:len(DB_NAME) - 3]
    dt_stamp = get_timestamp()

    db_backup = '{}-{}{}'.format(db_name_no_ext,
                                 dt_stamp, '.db')

    run('cp {} {}'.format(
        DB_NAME, db_backup
    ))

    run('mv {} {}/db-backups'.format(db_backup, SITE_FOLDER))


def _production_config():
    # use sed to make sure the server is set to production

    # this assumes that the script runs from the same local as app.py
    # which may not be a good idea
    sed("app.py", 'config.DevelopmentConfig',
        'config.ProductionConfig')


def _get_latest_source():
    if exists('.git'):
        run('git fetch')
    else:
        run(f'git clone {REPO_URL} .')
    current_commit = local("git log -n 1 --format=%H", capture=True)
    run(f'git reset --hard {current_commit}')


def _update_virtualenv():
    if not exists('photoenv/bin/pip'):
        run(f'python3.5 -m venv photoenv')
    run('./photoenv/bin/pip install -r requirements.txt')


def _restart_gunicorn():
    """
    Trying to get gunicorn to restart, I don't know if I need to restart nginx also.
    """
    # reloads services - see if this works first.
    # Seems to work ok, although browser cache is a problem.
    # this isn't enough at all...
    run(f'echo {SERVER_PASSWORD} | sudo -S systemctl daemon-reload')
    # You have the Gunicorn service saved like this:
    run(f'echo {SERVER_PASSWORD} | sudo -S systemctl restart app.service')
    # does it actually run it? seems ok
    # run(f'echo {SERVER_PASSWORD} | sudo -S ls -alh')


# command to deploy:
# fab deploy:host=
# fab deploy:host=
def deploy():
    with cd(SITE_FOLDER):
        _get_database_backups()
        _get_latest_source()
        _production_config()
        _restart_gunicorn()


if __name__ == "__main__":
    _production_config()
