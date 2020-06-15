from flask import Flask

app = Flask(__name__)


@app.route("/path", methods=['GET'])
def main():
    print("Hello world!")

    # TODO: Run full_run.py here


if __name__ == '__main__':
    app.run()
