from flask import Flask, request

app = Flask(__name__)


class MultOp:
  def __init__(self, xin, yin) -> None:
    self.xin = xin
    self.yin = yin
    self.result = None

  def cal(self):
    self.result = self.xin * self.yin

  def to_json(self):
    return {
      'xin': self.xin,
      'yin': self.yin,
      'result': self.result
    }


@app.route('/', methods=['GET'])
def greet():
  return {'message': 'Hello World!'}, 200


@app.route('/chat/<username>', methods=['GET'])
def greet_with_info(username):  # retrieve username from URL path
  # retrieve institution from URL query
  institution = request.args.get('institution', None)
  institution_segment = f' from {institution}' if institution else ''
  msg = f'Hello {username}{institution_segment}!'
  return {'message': msg}, 200


@app.route('/calculator/mult', methods=['POST'])
def mult():
  inputs = request.get_json()
  op = MultOp(xin=inputs['xin'], yin=inputs['yin'])
  op.cal()
  return op.to_json(), 200


if __name__ == '__main__':
  app.run(port=8081, debug=True)
