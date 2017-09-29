import enum
import uuid
from app import db

from sqlalchemy.dialects.postgresql import (
    UUID,
    JSON
)


class EventType(db.Model):
    __tablename__ = 'event_types'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    old_id = db.Column(db.Integer)
    event_type = db.Column(db.String(255), unique=True, nullable=False)
    event_desc = db.Column(db.String())
    event_filename = db.Column(db.String(255))
    duration = db.Column(db.Integer)
    repeat = db.Column(db.Integer)
    repeat_interval = db.Column(db.Integer)

    def serialize(self):
        return {
            'id': str(self.id),
            'event_type': self.event_type,
            'event_desc': self.event_desc,
            'event_filename': self.event_filename,
            'duration': self.duration,
            'repeat': self.repeat,
            'repeat_interval': self.repeat_interval
        }


class Fee(db.Model):
    __tablename__ = 'fees'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fee = db.Column(db.Integer, nullable=False)
    conc_fee = db.Column(db.Integer, nullable=False)
    multi_day_fee = db.Column(db.Integer, nullable=True)
    multi_day_conc_fee = db.Column(db.Integer, nullable=True)
    valid_from = db.Column(db.Date, nullable=True)
    event_type_id = db.Column(UUID(as_uuid=True), db.ForeignKey('event_types.id'), nullable=False)
    event_type = db.relationship(EventType, backref=db.backref("fees"))

    def serialize(self):
        return {
            'id': str(self.id),
            'event_type_id': str(self.event_type_id),
            'fee': self.fee,
            'conc_fee': self.conc_fee,
            'multi_day_fee': self.multi_day_fee,
            'multi_day_conc_fee': self.multi_day_conc_fee,
            'valid_from': self.valid_from.isoformat() if self.valid_from else None
        }


class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    old_id = db.Column(db.Integer)
    title = db.Column(db.String(255))
    sub_title = db.Column(db.String(255))
    description = db.Column(db.String())
    booking_code = db.Column(db.String(20))
    image_filename = db.Column(db.String(255))

    def serialize(self):
        return {
            'id': self.id,
            'old_id': self.old_id,
            'title': self.title,
            'sub_title': self.sub_title,
            'description': self.description,
            'booking_code': self.booking_code,
            'image_filename': self.image_filename
        }

    def __repr__(self):
        return '<Event: id {}>'.format(self.id)
