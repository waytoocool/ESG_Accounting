from ..extensions import db

# Association table for entity-data point relationship
entity_data_point = db.Table('entity_data_point',
    db.Column('entity_id', db.Integer, db.ForeignKey('entity.id'), primary_key=True),
    db.Column('data_point_id', db.Integer, db.ForeignKey('data_point.id'), primary_key=True)
)

class DataPoint(db.Model):
    """Data Point model for ESG metrics."""
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    value_type = db.Column(db.String(10), nullable=False)
    unit = db.Column(db.String(10), nullable=True)
    framework_id = db.Column(db.Integer, db.ForeignKey('framework.id'), nullable=False)
    
    # Relationships
    esg_data = db.relationship('ESGData', backref='data_point')

    def __init__(self, name, value_type, framework_id, unit=None):
        self.name = name
        self.value_type = value_type
        self.framework_id = framework_id
        self.unit = unit

    def __repr__(self):
        return f'<DataPoint {self.name}>'
