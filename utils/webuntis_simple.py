# Minimal WebUntis helper based on the provided script
# Credentials are no longer hardcoded. Pass server, school, username, password to fetch_timetable.
USERAGENT = "py-webuntis-example"

from datetime import date
import logging


def minutes_or_hhmm_to_str(val):
    if val is None:
        return None
    try:
        v = int(val)
    except Exception:
        return str(val)
    if v > 2400:
        hours = v // 60
        minutes = v % 60
    else:
        hours = v // 100
        minutes = v % 100
    return f"{hours:02d}:{minutes:02d}"


def value_from_period(period, key):
    try:
        v = getattr(period, key)
        if v is not None:
            return v
    except Exception:
        pass
    try:
        data = getattr(period, '_data', None)
        if isinstance(data, dict) and key in data:
            return data[key]
    except Exception:
        pass
    try:
        if isinstance(period, dict) and key in period:
            return period.get(key)
    except Exception:
        pass
    return None


def ids_for(period, field_name):
    items = value_from_period(period, field_name) or []
    ids = []
    for it in items:
        if isinstance(it, dict):
            ids.append(it.get('id'))
        else:
            ids.append(getattr(it, 'id', None))
    return [i for i in ids if i is not None]


def try_fetch(session, method_names):
    for name in method_names:
        try:
            fetch = getattr(session, name)
        except Exception:
            continue
        try:
            items = fetch()
            return items
        except Exception:
            continue
    return []


def get_id(it):
    if it is None:
        return None
    try:
        v = getattr(it, 'id', None)
        if v is not None:
            return v
    except Exception:
        pass
    try:
        data = getattr(it, '_data', None) or {}
        if isinstance(data, dict) and 'id' in data:
            return data.get('id')
    except Exception:
        pass
    try:
        if isinstance(it, dict):
            return it.get('id')
    except Exception:
        pass
    return None


def get_name(it):
    if it is None:
        return None
    data = getattr(it, '_data', None) or {}
    # try common name fields
    for key in ('name', 'longname', 'longName'):
        try:
            v = getattr(it, key, None) or data.get(key)
            if v:
                return v
        except Exception:
            pass
    # first+last
    try:
        fn = getattr(it, 'firstName', None) or data.get('firstName')
        ln = getattr(it, 'lastName', None) or data.get('lastName')
        if fn or ln:
            return f"{(fn or '').strip()} {(ln or '').strip()}".strip()
    except Exception:
        pass
    # fallback to string
    try:
        return str(it)
    except Exception:
        return None


def build_master_map(session, fetch_method_names, id_attr='id'):
    mapping = {}
    items = try_fetch(session, fetch_method_names)
    for it in items:
        try:
            key = get_id(it)
            name = get_name(it)
            if key is not None:
                mapping[key] = name
        except Exception:
            continue
    return mapping


def fetch_single(session, method_names, obj_id):
    for name in method_names:
        try:
            fn = getattr(session, name)
        except Exception:
            continue
        # try calling with single id
        try:
            res = fn(obj_id)
            if res:
                return res
        except Exception:
            pass
        # try calling with list of ids
        try:
            res = fn([obj_id])
            if res:
                # if returns list, take first
                try:
                    return res[0]
                except Exception:
                    return res
        except Exception:
            pass
    return None


def period_to_dict(day_date, start_time, period, maps):
    start_raw = value_from_period(period, 'startTime')
    end_raw = value_from_period(period, 'endTime')
    start_str = minutes_or_hhmm_to_str(start_raw)
    end_str = minutes_or_hhmm_to_str(end_raw)

    subj_ids = ids_for(period, 'su')
    teacher_ids = ids_for(period, 'te')
    room_ids = ids_for(period, 'ro')
    class_ids = ids_for(period, 'kl')

    def names_for(ids, mapping):
        return [mapping.get(i) for i in ids if i in mapping]

    result = {
        'date': str(day_date),
        'start_time_slot': str(start_time),
        'start_raw': start_raw,
        'end_raw': end_raw,
        'start': start_str,
        'end': end_str,
        'id': value_from_period(period, 'id'),
        'code': value_from_period(period, 'code'),
        'lstext': value_from_period(period, 'lstext'),
        'activityType': value_from_period(period, 'activityType'),
        'subjects': subj_ids,
        'subjects_names': names_for(subj_ids, maps.get('subjects', {})),
        'teachers': teacher_ids,
        'teachers_names': names_for(teacher_ids, maps.get('teachers', {})),
        'rooms': room_ids,
        'rooms_names': names_for(room_ids, maps.get('rooms', {})),
        'classes': class_ids,
        'classes_names': names_for(class_ids, maps.get('classes', {})),
    }
    return result


def fetch_timetable(start=None, end=None, debug=False):
    """Fetch timetable for a given start/end date (date object or ISO string). If not provided, defaults to today."""
    try:
        from webuntis import Session
        from webuntis.errors import RemoteError
    except Exception as e:
        raise RuntimeError("Missing dependency 'webuntis'. Install it in the project's venv: python -m pip install webuntis") from e

    # enable verbose logging to help debugging network/response issues
    logging.basicConfig()
    logging.getLogger('webuntis').setLevel(logging.DEBUG)
    logging.getLogger('requests').setLevel(logging.DEBUG)
    logging.getLogger('urllib3').setLevel(logging.DEBUG)

    # normalize start/end
    if start is None:
        start = date.today()
    elif isinstance(start, str):
        start = date.fromisoformat(start)
    if end is None:
        end = start
    elif isinstance(end, str):
        end = date.fromisoformat(end)

    # credentials must be provided via environment or parameters; try to read optional kwargs
    # allow fetch_timetable to receive creds via global variables set by caller
    try:
        server = fetch_timetable._server
        school = fetch_timetable._school
        username = fetch_timetable._username
        password = fetch_timetable._password
    except AttributeError:
        server = None; school = None; username = None; password = None

    if not server or not school or not username or not password:
        raise RuntimeError('WebUntis credentials not provided for fetch_timetable')

    # create session object so we can tweak headers and inspect on error
    sess = Session(server=server, school=school, username=username,
                   password=password, useragent=USERAGENT)
    try:
        # ensure requests session uses our User-Agent
        try:
            sess.session.headers.update({'User-Agent': USERAGENT})
        except Exception:
            pass

        sess.login()
    except Exception as e:
        import traceback, sys
        print('WebUntis login failed:')
        traceback.print_exc()
        # try one raw request for extra info if possible
        try:
            raw = sess._request('authenticate', {'user': USERNAME})
            print('Raw authenticate response:', raw)
        except Exception:
            pass
        raise

    try:
        # initial masterdata maps
        teachers_map = build_master_map(sess, ['teachers'])
        subjects_map = build_master_map(sess, ['subjects'])
        rooms_map = build_master_map(sess, ['rooms'])
        classes_map = build_master_map(sess, ['klassen', 'classes'])

        maps = {
            'teachers': teachers_map,
            'subjects': subjects_map,
            'rooms': rooms_map,
            'classes': classes_map,
        }

        # Stundenplan des eingeloggten Nutzers für the requested range
        raw_table = sess.my_timetable(start=start, end=end)
        try:
            table = raw_table.to_table()
        except Exception:
            # if to_table fails, try to use the raw object directly
            table = raw_table

        if debug:
            # build a small diagnostic summary without passwords
            try:
                table_len = len(table) if hasattr(table, '__len__') else 'unknown'
            except Exception:
                table_len = 'error'
            diag = {
                'logged_in': True,
                'server': server,
                'school': school,
                'username': username,
                'table_len': table_len,
            }
            # attempt to collect a small sample of the table contents
            try:
                sample = []
                for i, item in enumerate(table):
                    if i > 10:
                        break
                    sample.append(str(item))
                diag['table_sample'] = sample
            except Exception:
                diag['table_sample'] = 'unavailable'
            return diag

        # Sammle alle IDs, die auftauchen
        needed = {'teachers': set(), 'subjects': set(), 'rooms': set(), 'classes': set()}
        for start_time, day_entries in table:
            for day_date, period_set in day_entries:
                for period in period_set:
                    for t in ids_for(period, 'te'):
                        if t not in maps['teachers']:
                            needed['teachers'].add(t)
                    for su in ids_for(period, 'su'):
                        if su not in maps['subjects']:
                            needed['subjects'].add(su)
                    for r in ids_for(period, 'ro'):
                        if r not in maps['rooms']:
                            needed['rooms'].add(r)
                    for kl in ids_for(period, 'kl'):
                        if kl not in maps['classes']:
                            needed['classes'].add(kl)

        # Versuche fehlende IDs einzeln nachzuladen
        if needed['teachers']:
            for tid in list(needed['teachers']):
                obj = fetch_single(sess, ['teacher', 'getTeacher', 'get_teacher'], tid)
                if obj:
                    maps['teachers'][get_id(obj)] = get_name(obj)
        if needed['subjects']:
            for sid in list(needed['subjects']):
                obj = fetch_single(sess, ['subject', 'getSubject', 'get_subject'], sid)
                if obj:
                    maps['subjects'][get_id(obj)] = get_name(obj)
        if needed['rooms']:
            for rid in list(needed['rooms']):
                obj = fetch_single(sess, ['room', 'getRoom', 'get_room'], rid)
                if obj:
                    maps['rooms'][get_id(obj)] = get_name(obj)
        if needed['classes']:
            for cid in list(needed['classes']):
                obj = fetch_single(sess, ['klasse', 'getKlasse', 'get_klasse', 'class', 'getClass'], cid)
                if obj:
                    maps['classes'][get_id(obj)] = get_name(obj)

        output = []
        for start_time, day_entries in table:
            for day_date, period_set in day_entries:
                for period in period_set:
                    entry = period_to_dict(day_date, start_time, period, maps)
                    output.append(entry)

        return output
    finally:
        try:
            sess.logout()
        except Exception:
            pass


def fetch_timetable_default():
    return fetch_timetable()


def set_default_credentials(server, school, username, password):
    """Setze Module-weit Default-Credentials für convenience (nicht persistent)."""
    fetch_timetable._server = server
    fetch_timetable._school = school
    fetch_timetable._username = username
    fetch_timetable._password = password
    return True


if __name__ == '__main__':
    import json
    entries = fetch_timetable_default()
    print(json.dumps(entries, ensure_ascii=False, indent=2))
    try:
        with open('timetable.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps(entries, ensure_ascii=False, indent=2))
    except Exception:
        pass
