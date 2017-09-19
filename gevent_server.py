from gevent.wsgi import WSGIServer
from map_app import app

import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run CUER map server.')
    parser.add_argument('-p', '--port', action='store', default=5000)
    args = parser.parse_args()

    print("Starting server on port {}".format(int(args.port)))
    http_server = WSGIServer(('', args.port), app)
    http_server.serve_forever()
