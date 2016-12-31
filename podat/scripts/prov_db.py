# prov_db.py
#
# Store general procedures for interacting with the prov database
#

class ProvDB(object):
    @classmethod
    def get_crimes(cls, pgConnect, columns=["*"], limit=20):
        colStr = ", ".join(columns)
        selectStr = """SELECT {0} FROM prov_crime AS pc JOIN prov_statute AS ps ON pc.statute_id = ps.id JOIN prov_location AS pl ON pc.location_id = pl.id WHERE pl.latitude <> 0 ORDER BY pc.reported_date LIMIT {1};""".format(colStr, str(limit))

        return pgConnect.execute_select(selectStr)

    @classmethod
    def get_api_key(cls, pgConnect, selector):
        selectStr = """SELECT key FROM prov_api_keys WHERE name = {0} LIMIT 1;"""
        key = None

        if selector == "mapbox":
            entry = pgConnect.execute_select(selectStr.format("'mapbox'"))
            if len(entry) == 1:
                key = entry[0]["key"]

        return key
