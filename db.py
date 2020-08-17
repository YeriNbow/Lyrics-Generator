import pymysql


class ScrapeDB:
    """
    Save lyrics to MySQL Database
    """
    def __init__(self):
        self.con = pymysql.connect(host='127.0.0.1', user='root', password='******************',
                                   db='testdb', cursorclass=pymysql.cursors.DictCursor)
        self.curs = self.con.cursor()

    def create_table(self):
        sql = '''
                CREATE table IF NOT EXISTS scrape_tb(
                    Artist varchar(50),
                    Url varchar(200),
                    Title varchar(200),
                    Lyrics varchar(5000)
                );
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

    def get_data(self):
        sql = '''
            SELECT *
            FROM scrape_tb
            '''
        self.curs.execute(sql)

        return self.curs.fetchall()
