from ..extensions import db

class ESGData(db.Model):
    """ESG Data model for storing actual metric values."""
    
    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(50), nullable=False)
    metric = db.Column(db.String(50), nullable=False)
    value = db.Column(db.Float, nullable=True)
    entity_id = db.Column(db.Integer, db.ForeignKey('entity.id'), nullable=False)
    data_point_id = db.Column(db.Integer, db.ForeignKey('data_point.id'), nullable=False)

    def __init__(self, account, metric, value, entity_id, data_point_id):
        self.account = account
        self.metric = metric
        self.value = value
        self.entity_id = entity_id
        self.data_point_id = data_point_id

    def __repr__(self):
        return f'<ESGData {self.metric}: {self.value}>'
