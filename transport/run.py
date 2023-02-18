# from waitress import serve
# from . import create_app
# serve(create_app(), host='0.0.0.0', port=8080)
import create_app

if __name__=='__main__':
    app = create_app()
    app.run(host='0.0.0.0')