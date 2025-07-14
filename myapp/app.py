from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
  return {
    'message': 'hola, Mundo!!!'
  }

@app.route('/despedirse')
def bye_world():
  return {
    'message': 'Adiós, mundo!!!'
  }


app.run()