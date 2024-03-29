import os

from flask import Flask
from . import db
from . import auth
from . import blog
from . import inventory
from . import product
from . import material


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

    @app.route('/hello')
    def hello():
        return 'Hello, Worlds!'


    db.init_app(app)
    app.register_blueprint(auth.bp)


    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')


    app.register_blueprint(inventory.bp)


    app.register_blueprint(product.bp)


    app.register_blueprint(material.bp)

    from . import carriage
    app.register_blueprint(carriage.bp)

    from . import customer
    app.register_blueprint(customer.bp)

    from . import seller
    app.register_blueprint(seller.bp)

    from . import sell_record
    app.register_blueprint(sell_record.bp)

    from . import supplier
    app.register_blueprint(supplier.bp)

    from . import chat
    app.register_blueprint(chat.bp)
    chat.init_app(app)

    return app
app=create_app()