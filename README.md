# DUNGEON-GAME
# Repl Auth Flask App

This is a basic Flask web application that demonstrates how to authenticate users using Repl Auth.

## Prerequisites

* A Replit account
* Basic knowledge of Flask and HTML

## Setup

1. Create a new Python repl on Replit.
2. Add the following code to `main.py`:

```python
from flask import Flask, render_template, request

app = Flask('app')

@app.route('/')
def hello_world():
  return render_template(
    'index.html',
    user_id=request.headers['X-Replit-User-Id'],
    user_name=request.headers['X-Replit-User-Name'],
    user_roles=request.headers['X-Replit-User-Roles']
  )

app.run(host='0.0.0.0', port=8080)
<!DOCTYPE html>
<html>
  <head>
    <title>Repl Auth</title>
  </head>
  <body>
    {% if user_id %}
    <h1>Hello, {{ user_name }}!</h1>
    <p>Your user id is {{ user_id }}.</p>
    {% else %}
    Hello! Please log in.
    <div>
      <script
        authed="location.reload()"
        src="https://auth.util.repl.co/script.js"
      ></script>
    </div>
    {% endif %}
  </body>
</html>
