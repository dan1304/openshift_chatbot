import sqlite3
def fetch_kbs_json():
    """
    fetch all record to json for grid.js
    """
    with sqlite3.connect('kbs.db') as conn:
        cur = conn.cursor()
        kbs = cur.execute("SELECT JSON_ARRAY(JSON_OBJECT('kbs_id', kbs_id, 'kbs_desc', kbs_desc, 'kbs_resolution', kbs_resolution, 'kbs_tag', kbs_tag)) FROM kbs").fetchall()
        conn.commit()
    return kbs

data = fetch_kbs_json()
print(type(data))