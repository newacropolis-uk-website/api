from app import db

from app.dao.articles_dao import dao_create_article
from app.dao.blacklist_dao import store_token
from app.dao.emails_dao import dao_create_email
from app.dao.events_dao import dao_create_event, dao_get_event_by_old_id
from app.dao.event_dates_dao import dao_create_event_date
from app.dao.event_types_dao import dao_create_event_type
from app.dao.fees_dao import dao_create_fee
from app.dao.marketings_dao import dao_create_marketing
from app.dao.members_dao import dao_create_member
from app.dao.reject_reasons_dao import dao_create_reject_reason
from app.dao.speakers_dao import dao_create_speaker
from app.dao.users_dao import dao_create_user
from app.dao.venues_dao import dao_create_venue
from app.models import (
    Article, Email, Event, EventDate, EventType, Fee, Marketing, Member, RejectReason, Speaker, User, Venue,
    EVENT
)


def create_event(
    title='test title',
    description='test description',
    event_type_id=None,
    fee=5,
    conc_fee=3,
    multi_day_fee=12,
    multi_day_conc_fee=10,
    old_id=1,
    event_dates=None,
    venue_id=None
):
    if not event_type_id:
        event_type = EventType.query.filter_by(event_type='workshop').first()
        if not event_type:
            event_type = create_event_type(event_type='workshop')
        event_type_id = str(event_type.id)

    if not venue_id:
        venue = Venue.query.first()
        if not venue:
            venue = create_venue()
        venue_id = str(venue.id)

    data = {
        'old_id': old_id,
        'event_type_id': event_type_id,
        'title': title,
        'description': description,
        'fee': fee,
        'conc_fee': conc_fee,
        'multi_day_fee': multi_day_fee,
        'multi_day_conc_fee': multi_day_conc_fee,
        'venue_id': venue_id,
    }
    event = Event(**data)

    if event_dates:
        event.event_dates.extend(event_dates)

    dao_create_event(event)

    return event


def create_event_type(
        old_id=1,
        event_type='talk',
        event_desc='test talk',
        event_filename=None,
        duration=45,
        repeat=1,
        repeat_interval=0
):
    data = {
        'old_id': old_id,
        'event_type': event_type,
        'event_desc': event_desc,
        'event_filename': event_filename,
        'duration': duration,
        'repeat': repeat,
        'repeat_interval': repeat_interval
    }
    event_type = EventType(**data)

    dao_create_event_type(event_type)
    return event_type


def create_event_date(
    event_id=None,
    event_datetime='2018-01-01 19:00',
    duration=90,
    soldout=False,
    repeat=3,
    repeat_interval=7,
    fee=5,
    conc_fee=3,
    multi_day_fee=12,
    multi_day_conc_fee=10,
    speakers=None,
):
    venue = create_venue()

    data = {
        'event_id': event_id,
        'event_datetime': event_datetime,
        'duration': duration,
        'soldout': soldout,
        'repeat': repeat,
        'repeat_interval': repeat_interval,
        'fee': fee,
        'conc_fee': conc_fee,
        'multi_day_fee': multi_day_fee,
        'multi_day_conc_fee': multi_day_conc_fee,
        'venue_id': venue.id,
    }

    event_date = EventDate(**data)

    if speakers:
        for s in speakers:
            event_date.speakers.append(s)

    dao_create_event_date(event_date)
    return event_date


def create_fee(event_type_id=None, fee=5, conc_fee=3, multi_day_fee=0, multi_day_conc_fee=0, valid_from=None):
    if not event_type_id:
        event_type = create_event_type(event_type='seminar')
        event_type_id = event_type.id

    data = {
        'event_type_id': event_type_id,
        'fee': fee,
        'conc_fee': conc_fee,
        'multi_day_fee': multi_day_fee,
        'multi_day_conc_fee': multi_day_conc_fee,
        'valid_from': valid_from
    }
    fee = Fee(**data)

    dao_create_fee(fee)
    return fee


def create_token_blacklist(sample_decoded_token):
    store_token(sample_decoded_token)
    return sample_decoded_token


def create_speaker(title='Mr', name='First Mid Last-name', parent_id=None):
    data = {
        'title': title,
        'name': name,
        'parent_id': parent_id
    }

    speaker = Speaker(**data)

    dao_create_speaker(speaker)
    return speaker


def create_venue(
    old_id='1',
    name='Head office',
    address='10 London Street, N1 1NN',
    directions='By bus: 100, 111, 123',
    default=True
):
    data = {
        'old_id': old_id,
        'name': name,
        'address': address,
        'directions': directions,
        'default': default
    }

    venue = Venue(**data)

    dao_create_venue(venue)
    return venue


def create_article(
        old_id=1,
        title='Egyptians',
        author='Mrs Black',
        content='Some info about Egypt\r\n\"Something in quotes\"',
):
    data = {
        'old_id': old_id,
        'title': title,
        'author': author,
        'content': content,
    }
    article = Article(**data)

    dao_create_article(article)
    return article


def create_email(
        old_id=1,
        old_event_id=2,
        event_id=None,
        details='test event details',
        extra_txt='test extra text',
        replace_all=False,
        email_type=EVENT,
        created_at=None,
        send_starts_at=None,
        expires=None
):
    if old_event_id:
        event = dao_get_event_by_old_id(old_event_id)
        if not event:
            event = create_event(old_id=old_event_id)
            create_event_date(event_id=str(event.id), event_datetime='2019-06-21 19:00')
        event_id = str(event.id)

    data = {
        'event_id': event_id,
        'old_id': old_id,
        'old_event_id': old_event_id,
        'details': details,
        'extra_txt': extra_txt,
        'replace_all': replace_all,
        'email_type': email_type,
        'created_at': created_at,
        'send_starts_at': send_starts_at,
        'expires': expires
    }
    email = Email(**data)

    dao_create_email(email)
    return email


def create_marketing(
    old_id=None,
    description='Poster',
    order_number=0,
    active=True,
):
    data = {
        'old_id': old_id,
        'description': description,
        'order_number': order_number,
        'active': active,
    }

    marketing = Marketing(**data)

    dao_create_marketing(marketing)

    return marketing


def create_member(
    old_id=1,
    name='Joe Blue',
    email='test@example.com',
    active=True,
    old_marketing_id=1,
    is_course_member=False,
    last_updated=None,
    marketing_id=None
):
    if not marketing_id:
        search_marketing = Marketing.query.filter_by(description='Search').first()
        if not search_marketing:
            marketing = create_marketing(description='Search')
            marketing_id = str(marketing.id)
        else:
            marketing_id = str(search_marketing.id)

    data = {
        'old_id': old_id,
        'name': name,
        'email': email,
        'active': active,
        'old_marketing_id': old_marketing_id,
        'is_course_member': is_course_member,
        'last_updated': last_updated,
        'marketing_id': marketing_id
    }

    member = Member(**data)

    dao_create_member(member)

    return member


def create_user(email='test@example.com', name='First Mid Last-name', access_area=',email,event,report,article,'):
    data = {
        'email': email,
        'name': name,
        'active': True,
        'access_area': access_area,
    }

    user = User(**data)

    dao_create_user(user)
    return user


def create_reject_reason(event_id=None, reason='Test reason', resolved=False, created_by=None):
    if not created_by:
        created_by = create_user(email='test_reject@example.com')

    data = {
        'event_id': event_id,
        'reason': reason,
        'resolved': resolved,
        'created_by': str(created_by.id)
    }

    reject_reason = RejectReason(**data)

    dao_create_reject_reason(reject_reason)

    return reject_reason
