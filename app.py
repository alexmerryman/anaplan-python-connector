from flask import Flask

app = Flask(__name__)


@app.route("/path", methods=['GET'])
def main():
    print("Hello world!")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5001')
