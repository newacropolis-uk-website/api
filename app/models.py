import datetime
import uuid
import re

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import UniqueConstraint
from sqlalchemy.ext.hybrid import hybrid_property

from app import db


class TokenBlacklist(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    jti = db.Column(db.String(36), nullable=False)
    token_type = db.Column(db.String(10), nullable=False)
    user_identity = db.Column(db.String(50), nullable=False)
    revoked = db.Column(db.Boolean, nullable=False)
    expires = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def serialize(self):
        return {
            'token_id': self.id,
            'jti': self.jti,
            'token_type': self.token_type,
            'user_identity': self.user_identity,
            'revoked': self.revoked,
            'expires': self.expires
        }


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
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def serialize(self):
        def fees():
            _fees = []
            for fee in self.fees:
                _fees.append({
                    'fee': fee.fee,
                    'conc_fee': fee.conc_fee,
                    'valid_from': fee.valid_from.isoformat()
                })

            _fees = sorted(_fees, key=lambda f: f['valid_from'], reverse=True)
            return _fees

        return {
            'id': str(self.id),
            'old_id': self.old_id,
            'event_type': self.event_type,
            'event_desc': self.event_desc,
            'event_filename': self.event_filename,
            'duration': self.duration,
            'repeat': self.repeat,
            'repeat_interval': self.repeat_interval,
            'fees': fees(),
            'created_at': self.created_at
        }


class Fee(db.Model):
    __tablename__ = 'fees'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fee = db.Column(db.Integer, nullable=False)
    conc_fee = db.Column(db.Integer, nullable=False)
    multi_day_fee = db.Column(db.Integer, nullable=True)
    multi_day_conc_fee = db.Column(db.Integer, nullable=True)
    valid_from = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    event_type_id = db.Column(UUID(as_uuid=True), db.ForeignKey('event_types.id'), nullable=False)
    event_type = db.relationship(EventType, backref=db.backref("fees", order_by=valid_from.desc()))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def serialize(self):
        return {
            'id': str(self.id),
            'event_type_id': str(self.event_type_id),
            'fee': self.fee,
            'conc_fee': self.conc_fee,
            'multi_day_fee': self.multi_day_fee,
            'multi_day_conc_fee': self.multi_day_conc_fee,
            'valid_from': self.valid_from.isoformat()
        }


class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    old_id = db.Column(db.Integer)
    duration = db.Column(db.Integer, nullable=True)
    event_type_id = db.Column(UUID(as_uuid=True), db.ForeignKey('event_types.id'), nullable=False)
    event_type = db.relationship("EventType", backref=db.backref("event", uselist=False))
    title = db.Column(db.String(255))
    sub_title = db.Column(db.String(255))
    description = db.Column(db.String())
    booking_code = db.Column(db.String(20))
    image_filename = db.Column(db.String(255))
    fee = db.Column(db.Integer, nullable=True)
    conc_fee = db.Column(db.Integer, nullable=True)
    multi_day_fee = db.Column(db.Integer, nullable=True)
    multi_day_conc_fee = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    event_dates = db.relationship("EventDate", backref=db.backref("events"), cascade="all,delete,delete-orphan")
    venue_id = db.Column(UUID(as_uuid=True), db.ForeignKey('venues.id'))
    venue = db.relationship("Venue", backref=db.backref("event", uselist=False))

    def serialize(self):
        def sorted_event_dates():
            dates = [e.serialize() for e in self.event_dates]
            dates.sort(key=lambda k: k['event_datetime'])
            return dates

        return {
            'id': self.id,
            'old_id': self.old_id,
            'event_type': self.event_type.event_type,
            'event_type_id': self.event_type.id,
            'title': self.title,
            'sub_title': self.sub_title,
            'description': self.description,
            'booking_code': self.booking_code,
            'image_filename': self.image_filename,
            'fee': self.fee,
            'conc_fee': self.conc_fee,
            'multi_day_fee': self.multi_day_fee,
            'multi_day_conc_fee': self.multi_day_conc_fee,
            'venue': self.venue.serialize() if self.venue else None,
            'event_dates': sorted_event_dates()
        }

    def __repr__(self):
        return '<Event: id {}>'.format(self.id)


class Speaker(db.Model):
    __tablename__ = 'speakers'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = db.Column(db.String(100))
    name = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    # should only expect 1 parent at most, so a parent cannot be a parent
    parent_id = db.Column(UUID(as_uuid=True), primary_key=False, default=None, nullable=True)

    def serialize(self):
        return {
            'id': str(self.id),
            'title': self.title,
            'name': self.name,
            'parent_id': str(self.parent_id) if self.parent_id else None
        }

    @hybrid_property
    def last_name(self):
        return str(self.name).split(' ')[-1]


event_date_to_speaker = db.Table(
    'event_date_to_speaker',
    db.Model.metadata,
    db.Column('event_date_id', UUID(as_uuid=True), db.ForeignKey('event_dates.id')),
    db.Column('speaker_id', UUID(as_uuid=True), db.ForeignKey('speakers.id')),
    UniqueConstraint('event_date_id', 'speaker_id', name='uix_event_date_id_to_speaker_id')
)


class EventDate(db.Model):
    __tablename__ = 'event_dates'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = db.Column(UUID(as_uuid=True), db.ForeignKey('events.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    event_datetime = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    end_time = db.Column(db.Time, nullable=True)
    duration = db.Column(db.Integer, nullable=True)
    soldout = db.Column(db.Boolean, default=False)
    repeat = db.Column(db.Integer, nullable=True)
    repeat_interval = db.Column(db.Integer, nullable=True)
    fee = db.Column(db.Integer, nullable=True)
    conc_fee = db.Column(db.Integer, nullable=True)
    multi_day_fee = db.Column(db.Integer, nullable=True)
    multi_day_conc_fee = db.Column(db.Integer, nullable=True)

    venue_id = db.Column(UUID(as_uuid=True), db.ForeignKey('venues.id'))
    venue = db.relationship("Venue", backref=db.backref("event_date", uselist=False))
    speakers = db.relationship(
        'Speaker',
        secondary=event_date_to_speaker,
        backref=db.backref('event_date_to_speaker', lazy='dynamic'),
        cascade="delete"
    )

    def serialize(self):
        return {
            'id': str(self.id),
            'event_id': str(self.event_id),
            'event_datetime': self.event_datetime.strftime('%Y-%m-%d %H:%M'),
            'end_time': self.end_time.strftime('%H:%M') if self.end_time else None,
            'speakers': [s.serialize() for s in self.speakers]
        }


class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    old_id = db.Column(db.Integer)
    name = db.Column(db.String(255))
    address = db.Column(db.String(255))
    directions = db.Column(db.String(255))

    default = db.Column(db.Boolean)

    def serialize(self):
        return {
            'id': str(self.id),
            'old_id': self.old_id,
            'name': str(self.name),
            'address': self.address,
            'directions': self.directions,
            'default': self.default,
        }


class Article(db.Model):
    __tablename__ = 'articles'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    old_id = db.Column(db.Integer)
    title = db.Column(db.String(255))
    author = db.Column(db.String(255))
    content = db.Column(db.Text())
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def serialize(self):
        return {
            'id': str(self.id),
            'old_id': self.old_id,
            'title': self.title,
            'author': self.author,
            'content': self.content,
            'created_at': self.created_at.strftime('%Y-%m-%d') if self.created_at else None,
        }

    def serialize_summary(self):
        def get_short_content(num_words):
            html_tag_pattern = r'<.*?>'
            clean_content = re.sub(html_tag_pattern, '', self.content)

            content_arr = clean_content.split(' ')
            if len(content_arr) > num_words:
                find_words = " ".join([content_arr[num_words - 2], content_arr[num_words - 1], content_arr[num_words]])
                return clean_content[0:clean_content.index(find_words) + len(find_words)] + '...'
            else:
                return clean_content

        return {
            'id': str(self.id),
            'title': self.title,
            'author': self.author,
            'short_content': get_short_content(num_words=110),
            'very_short_content': get_short_content(num_words=30),
        }


ACCESS_AREAS = ['email', 'event', 'report', 'article']
USER_ADMIN = 'admin'


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=True)
    active = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    last_login = db.Column(db.DateTime)
    access_area = db.Column(db.String())
    session_id = db.Column(db.String())
    ip = db.Column(db.String())

    def serialize(self):
        return {
            'id': str(self.id),
            'email': self.email,
            'name': self.name,
            'active': self.active,
            'created_at': self.created_at,
            'last_login': self.last_login,
            'access_area': self.access_area,
            'session_id': self.session_id,
            'ip': self.ip
        }

    def is_admin(self):
        return self.access_area == USER_ADMIN
