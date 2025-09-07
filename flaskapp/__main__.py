from flaskapp.app import app

# This will need to be updated to 5001 if running a separate flask instance on machine
PORT_NUMBER = 5000

app.run(debug=True, port=PORT_NUMBER)