def get_nice_event_dates(event_dates):
    event_date_str = ''
    _event_month = ''
    _event_dates = ''
    for event_date in event_dates:
        m = event_date.event_datetime.strftime("%B")
        d = event_date.event_datetime.strftime("%a %-d, ")

        if not _event_month:
            _event_month = event_date.event_datetime.strftime("%B")

        if m == _event_month:
            _event_dates += d
        elif _event_dates:
            event_date_str += _event_dates[:-2] + ' of ' + _event_month + ', '
            _event_dates = d
            _event_month = m

    event_date_str = (event_date_str if len(event_date_str) > 2 else '') + _event_dates[:-2] + ' of ' + _event_month
    event_datetime = event_dates[0].event_datetime
    event_date_str += ' - ' + event_datetime.strftime(
        "%-I:%M %p" if event_datetime.strftime("%M") != '00' else "%-I %p")

    return event_date_str
