# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from flask import Flask

import auth
from db import *
from auth import *
from blog import *
from inventory import *
from product import *
from material import *
from carriage import *
from customer import *
from seller import *
from sell_record import *


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'transport.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass


    db.init_app(app)


    app.register_blueprint(auth.authBp)


    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')


    app.register_blueprint(inventory.bp)


    app.register_blueprint(product.bp)


    app.register_blueprint(material.bp)


    app.register_blueprint(carriage.bp)


    app.register_blueprint(customer.bp)


    app.register_blueprint(seller.bp)


    app.register_blueprint(sell_record.bp)

    return app

app = create_app()
if __name__=='__main__':

    app.run(host='0.0.0.0')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
