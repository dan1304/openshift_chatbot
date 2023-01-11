import sqlite3
import pandas as pd
from rapidfuzz import process, fuzz
from kbs.models import Kbs
from app import db

class KnowledgeBase:
    def __init__(self) -> None:
        pass
        

    def get_kbs(error_keywords):
        """
        Compare the error_keywords (use input) with kbs in database
        Return the most matched resolution
        """

        conn = sqlite3.connect('./kbs/kbs.db')  
        sql_kbs_query = pd.read_sql_query ('''
                               SELECT
                               kbs_desc
                               FROM kbs
                               ''', conn)

        
        # Convert all kbs_desc from kbs schema to a dataframe
        # Return the 1D list of kbs, then it can be used for matching using rapidfuzz 
        kbs_df = pd.DataFrame(sql_kbs_query)
        kbs_df_data = kbs_df.values.flatten().tolist()

        result = process.extract(error_keywords, kbs_df_data, scorer=fuzz.WRatio, limit=1)
        if result[0][1] > 88:
            kbs_desc = result[0][0]
            with sqlite3.connect('./kbs/kbs.db') as conn:
                cur = conn.cursor()
                cur.execute("SELECT kbs_resolution FROM kbs where kbs_desc = ?", (kbs_desc,))
                kbs_resolution = cur.fetchone()
            conn.close()
            return kbs_resolution
        else:
            return "No knowledgebase found for your keywords. You can submit a new one at https://act-bot.public-thn.ascendmoney.io/kbs/"

    #TODO: filter search
    def filter_panda(search):
        kbs = Kbs.query
        filter_kbs = kbs.filter(db.or_(
                                        Kbs.kbs_desc.like(f'%{search}%'),
                                        Kbs.kbs_resolution.like(f'%{search}%')
                                ))
        kbs_df = pd.DataFrame([kb.to_dict() for kb in filter_kbs])
        kbs_df_data = kbs_df.values.flatten().tolist()

        import ipdb; ipdb.set_trace()

        total = filter_kbs.count()
        result = process.extract(search, kbs_df_data, scorer=fuzz.WRatio, limit=1)

        return {
                'data': [kb.to_dict() for kb in filter_kbs],
                'total': total,
                }



    def create_new_kbs(kbs_desc, kbs_resolution, kbs_tag):
        """
        Create a new knowledge base
        """
        new_kb = Kbs(kbs_desc, kbs_resolution, kbs_tag)
        print(kbs_desc, kbs_resolution, kbs_tag)
        # import ipdb; ipdb.set_trace()
        db.session.add(new_kb)
        db.session.commit()

    
    def update_kb(data):
        """
        Update knowledge record
        """
        kb = Kbs.query.get(int(data['id']))
        for field in ['kbs_desc', 'kbs_resolution', 'kbs_tag']:
            if field in data:
                setattr(kb, field, data[field])
        db.session.commit()
        return '', 204


    def fetch_kbs_json():
        """
        Fetch all kb records
        """
        # import ipdb; ipdb.set_trace()
        kbs_list = Kbs.query.order_by(Kbs.kbs_id).all()
        total = Kbs.query.count()
        return {'data': [kb.to_dict() for kb in kbs_list],
                'total': total}


    def filter_kbs(search):
        """
        filter kbs for searching
        """
        kbs = Kbs.query
        filter_kbs = kbs.filter(db.or_(
                                        Kbs.kbs_desc.like(f'%{search}%'),
                                        Kbs.kbs_resolution.like(f'%{search}%')
                                ))
        total = filter_kbs.count()
        return {
                'data': [kb.to_dict() for kb in filter_kbs],
                'total': total,
                }
    
    def pagination(start_page, length_offset):
        """
        Paging the kbs table
        """
        kbs = Kbs.query
        if start_page != -1 and length_offset != -1:
            kbs_in_page = kbs.offset(start_page).limit(length_offset)
        total = kbs_in_page.count()
        return {
        'data': [kb.to_dict() for kb in kbs_in_page],
        'total': total,
        }
