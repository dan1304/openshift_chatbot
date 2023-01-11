import sqlite3
import pandas as pd
from rapidfuzz import process, fuzz




conn = sqlite3.connect('kbs.db') 
          
sql_kbs_query = pd.read_sql_query ('''
                               SELECT
                               kbs_desc
                               FROM kbs
                               ''', conn)

kbs_df = pd.DataFrame(sql_kbs_query)
kbs_df_data = kbs_df.values.flatten().tolist()

input = '''Path does not chain with any of the trust anchors'''
result = process.extract(input, (kbs_df_data), scorer=fuzz.WRatio, limit=1)
print(result)
if result[0][1] > 88:
    kbs_desc = result[0][0]
    with sqlite3.connect('kbs.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT kbs_resolution FROM kbs where kbs_desc = ?", (kbs_desc,))
        kbs_resolution = cur.fetchone()
    conn.close()
    print(kbs_resolution)

