from app import app, db

# Create an application context
app.app_context().push()

# Create the database tables
db.create_all()
