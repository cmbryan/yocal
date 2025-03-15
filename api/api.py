from . import create_app


app = create_app()

@app.route("/test")
def hello_world():
    return "<p>Hello, World!</p>"
