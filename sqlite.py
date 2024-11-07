import sqlite3 as sq


async def db_start():
    global db, cur

    db = sq.connect('BASE.db')
    cur = db.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS profile(user_id INTEGER PRIMARY KEY, name_group, notice_time, notice_status)")
    cur.execute("CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY, user_id, day, name_event, time_event)")
    db.commit()


async def edit_notif_time(time, user_id):
    cur.execute(f'UPDATE profile SET notice_time = "{time}" WHERE user_id = {user_id}')
    db.commit()


async def edit_notif_state(x, user_id):
    cur.execute(f'UPDATE profile SET notice_status = {x} WHERE user_id = {user_id}')
    db.commit()


async def get_user(user_id):
    user = cur.execute(f'SELECT * FROM profile WHERE user_id = "{user_id}"').fetchall()
    return user


async def get_profiles():
    profiles = cur.execute('SELECT * FROM profile').fetchall()
    return profiles


async def check_profile(user_id):

    smth = cur.execute(f"""
    SELECT name_group FROM profile WHERE user_id = "{user_id}"
    """).fetchall()

    return smth


async def add_profile(state, user_id):
    async with state.proxy() as data:
        cur.execute(f"INSERT INTO profile(user_id, name_group) "
                    f"VALUES('{user_id}','{data['name_group']}')")
        db.commit()


async def new_event(state, user_id):
    async with state.proxy() as data:
        cur.execute(f"INSERT INTO events(user_id, day, name_event, time_event) "
                    f"VALUES('{user_id}','{data['day']}', '{data['name_event']}', '{data['time_event']}')")
        db.commit()


async def get_week_events(user_id):

    events = cur.execute(f"""
    SELECT * FROM events WHERE user_id = "{user_id}"
    """).fetchall()
    return events


async def get_day_events(user_id, day):

    events = cur.execute(f"""
        SELECT * FROM events WHERE user_id = "{user_id}" AND day = "{day}"
        """).fetchall()
    return events


async def dell_event(id):
    cur.execute(f"""
    DELETE FROM events WHERE id = "{id}"
""")
    db.commit()
