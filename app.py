from flask import Flask, render_template, jsonify


from database_interface import Database


app = Flask(__name__)
app.config['DEBUG'] = True

db = Database('eigi-data.db')


tags = db.get_all_tags()

"""
$ export FLASK_APP=my_application
$ export FLASK_ENV=development
$ flask run
"""


@app.route('/')
def country_question():
    return render_template("base.html")


@app.route("/name/<name>")
def index(name):
    if name.lower() == "michael":
        return "Hello, {}".format(name), 200
    else:
        return "Not Found", 404


# @app.route("/")
# def hello():

#     tag_data = {
#         'tags': tags
#     }

#     return jsonify(tag_data)
if __name__ == '__main__':
    app.run()
