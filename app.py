# Flask
from flask import Flask, render_template

# User route import.
from user.user_routes import user_blueprint

# photo
from photo.photo_routes import photo_blueprint
from user.user_routes import user_blueprint
from upload.upload_routes import upload_blueprint
from album.album_routes import album_blueprint
from photo_tag.photo_tag_routes import photo_tag_blueprint


app = Flask(__name__)
# CONFIG = 'config.DevelopmentConfig'
CONFIG = 'config.ProductionConfig'
# Apply config values.

# config.DevelopmentConfig should change to config.ProductionConfig on deployment.
app.config.from_object(CONFIG)


# photo site
app.register_blueprint(photo_blueprint, url_prefix="/")
app.register_blueprint(photo_blueprint, url_prefix="/photo")
app.register_blueprint(user_blueprint, url_prefix="/user")
app.register_blueprint(upload_blueprint, url_prefix="/upload")
app.register_blueprint(album_blueprint, url_prefix="/photo/album")
app.register_blueprint(photo_tag_blueprint, url_prefix="/tag")
