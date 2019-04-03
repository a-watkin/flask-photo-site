from flask import Flask, render_template, request, session, flash, redirect, url_for


# User route import.
from photo.photo_routes import photo_blueprint
from user.user_routes import user_blueprint
from upload.upload_routes import upload_blueprint
from album.album_routes import album_blueprint
from photo_tag.photo_tag_routes import photo_tag_blueprint


app = Flask('app')
app = Flask(__name__.split('.')[0])

# Apply config values.
app.config.from_object('config.DevelopmentConfig')

# Register blueprints.
app.register_blueprint(photo_blueprint, url_prefix="/photo")
app.register_blueprint(user_blueprint, url_prefix="/photo/user")
app.register_blueprint(upload_blueprint, url_prefix="/upload")
app.register_blueprint(album_blueprint, url_prefix="/album")
app.register_blueprint(photo_tag_blueprint, url_prefix="/photo/tag")


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        debug=True
    )
