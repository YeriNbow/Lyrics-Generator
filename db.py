import pymysql


class ScrapeDB:
    """
    Save lyrics to MySQL Database
    """
    def __init__(self, user, password, db):
        self.con = pymysql.connect(host='127.0.0.1', user=user, password=password,
                                   db=db, cursorclass=pymysql.cursors.DictCursor)
        self.curs = self.con.cursor()

    def create_table(self):
        sql = '''
                CREATE table IF NOT EXISTS scrape_tb(
                    Artist varchar(50),
                    Url varchar(200),
                    Title varchar(200),
                    Lyrics varchar(5000)
                )
                '''
        self.curs.execute(sql)
        self.con.commit()

    def insert_data(self, artist, url, title, lyrics):
        sql = '''
                INSERT INTO scrape_tb
                values(%s, %s, %s, %s)
                '''
        self.curs.execute(sql, (artist, url, title, lyrics))
        self.con.commit()

    def get_all_data(self):
        sql = '''
            SELECT *
            FROM scrape_tb
            '''
        self.curs.execute(sql)

        return self.curs.fetchall()

    def get_data(self, artist):
        sql = '''
            SELECT *
            FROM scrape_tb
            WHERE artist = %s
            '''
        self.curs.execute(sql, artist)

        return self.curs.fetchall()

    def get_artist_list(self):
        sql = '''
            SELECT DISTINCT artist
            FROM scrape_tb
            '''
        self.curs.execute(sql)

        artist_list = [result['artist'] for result in self.curs.fetchall()]

        return artist_list
