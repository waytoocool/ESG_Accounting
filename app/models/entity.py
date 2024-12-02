from ..extensions import db
from .data_point import entity_data_point

class Entity(db.Model):
    """Entity model for organizational hierarchy."""
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    entity_type = db.Column(db.String(20), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('entity.id'), nullable=True)
    
    # Relationships
    parent = db.relationship('Entity', 
                           backref=db.backref('children', lazy='dynamic'),
                           remote_side=[id])
    users = db.relationship('User', backref='entity')
    data_points = db.relationship('DataPoint',
                                secondary=entity_data_point,
                                backref=db.backref('entities', lazy='dynamic'))
    esg_data = db.relationship('ESGData', backref='entity')

    def __init__(self, name, entity_type, parent_id=None):
        self.name = name
        self.entity_type = entity_type
        self.parent_id = parent_id

    def get_hierarchy_level(self):
        """Calculate the level of this entity in the hierarchy."""
        level = 1
        current = self
        while current.parent_id is not None:
            level += 1
            current = current.parent
        return level

    def __repr__(self):
        return f'<Entity {self.name}>'