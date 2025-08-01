import os
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    """Initializes the SQLAlchemy DB instance with the Flask app."""
    db.init_app(app)
    
    # Create instance directory with absolute path
    instance_path = os.path.join(app.root_path, 'instance')
    
    try:
        # Ensure instance directory exists with proper permissions
        os.makedirs(instance_path, exist_ok=True)
        print(f"Instance directory ready: {instance_path}")
        
        # Get the database path from the URI
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        if 'sqlite:///' in db_uri:
            db_path = db_uri.replace('sqlite:///', '')
            print(f"Database will be created at: {db_path}")
            
            # Ensure the database directory exists
            db_dir = os.path.dirname(db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
                print(f"Created database directory: {db_dir}")
        
    except Exception as e:
        print(f"Error setting up database directory: {e}")
        # Fallback to a simple path in the current directory
        fallback_path = os.path.join(app.root_path, 'users.db')
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{fallback_path}'
        print(f"Fallback: Using database at {fallback_path}")

    with app.app_context():
        try:
            # Create all database tables
            print("Creating database tables...")
            db.create_all()
            print("Database tables created successfully")
            
            # Verify database connection
            with db.engine.connect() as conn:
                conn.execute(db.text('SELECT 1'))
                print("Database connection verified")
                
        except Exception as e:
            print(f"Error during database initialization: {e}")
            print("This might be a permissions issue or invalid database path")
            raise
