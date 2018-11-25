from flask import Flask, render_template, request, session, flash, redirect, url_for, g

from functools import wraps


from database_interface import Database


app = Flask(__name__)
app.config['DEBUG'] = True


app.config['USERNAME'] = 'admin'
app.config['PASSWORD'] = 'admin'

SECRET_KEY = 'secret'

print(app.config.keys())

db = Database('eigi-data.db')


tags = db.get_all_tags()

"""
$ export FLASK_APP=my_application
$ export FLASK_ENV=development
$ flask run
"""


@app.route('/', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        username = request.form.get('username', None)
        password = request.form.get('password', None)
        print('\n', username, password)

        if username == app.config['USERNAME'] and password == app.config['PASSWORD']:
            return render_template('main.html')

    else:
        return render_template('login.html')


# with app.test_request_context():
#     print(url_for('login'))

# @app.route("/")
# def hello():

#     tag_data = {
#         'tags': tags
#     }

#     return jsonify(tag_data)


if __name__ == '__main__':
    app.run()
