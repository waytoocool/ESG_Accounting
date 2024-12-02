from ..extensions import db

class Framework(db.Model):
    """Framework model for ESG reporting frameworks."""
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    
    # Relationships
    data_points = db.relationship('DataPoint', backref='framework', lazy=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f'<Framework {self.name}>'
