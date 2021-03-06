from app import app

from app import app, db
from app.models import Provider, Truck, Rate

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Provider': Provider, 'Truck': Truck, 'Rate': Rate}