from flask import Flask
import os

app = Flask(__name__)


@app.route('/')
def hello():
  server_name = os.getenv('SERVER_NAME', 'Unknown Server')
  return f'Hello from {server_name}!'


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=int(os.getenv('FLASK_PORT', 5000)))
