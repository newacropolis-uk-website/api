import enum
from app import db


class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String())
    description = db.Column(db.String())
    date = db.Column(db.DateTime())

    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'date': self.date
        }

    def __repr__(self):
        return '<Event: id {}>'.format(self.id)
