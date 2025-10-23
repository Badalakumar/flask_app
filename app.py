from flask import Flask, render_template, request, redirect, url_for, flash
from db import db_connection
from auth import auth_ap
from admin import admin_ap

app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.register_blueprint(auth_ap)
app.register_blueprint(admin_ap, url_prefix='/admin')


if __name__ == '__main__':
 app.run(debug=True)
