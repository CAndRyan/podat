"""prov_db.py - Store general procedures for interacting with the prov database"""

# pylint: disable=C0301

class ProvDB(object):
    """An class containing stored procedures for the prov database"""

    @classmethod
    def get_crimes(cls, pg_connect, limit=20, from_dt=None, to_dt=None, columns=None):
        """Get full crime objects from the database"""
        if columns is None:
            columns = ["*"]
        if limit > 200:
            limit = 200
        if limit < 1:
            limit = 1

        col_str = ", ".join(columns)
        select_str = """SELECT {0} FROM prov_crime AS pc JOIN prov_statute AS ps ON pc.statute_id = ps.id JOIN prov_location AS pl ON pc.location_id = pl.id WHERE pl.latitude <> 0 ORDER BY pc.reported_date LIMIT {1};""".format(col_str, str(limit))

        return pg_connect.execute_select(select_str)

    @classmethod
    def get_api_key(cls, pg_connect, selector):
        """Get an API key, by name, from the database - restrict available sectors to protect the database"""
        select_str = """SELECT key FROM prov_api_keys WHERE name = '{0}' LIMIT 1;"""
        key = None

        if selector == "mapbox":
            entry = pg_connect.execute_select(select_str.format(selector))
            if len(entry) == 1:
                key = entry[0]["key"]

        return key
