# !python3 - scrapes bbc.com for any articles related to Africa
# opens these articles in your browser to view html content
# then collects and sdownloads their href into a DB for future reference


import webbrowser
import requests
import bs4
import html
import MySQLdb
import datetime


today_date = datetime.datetime.now().strftime('%Y-%m-%d')

# to create an africa table in your MySQL database

# CREATE TABLE test.africa(
# publish_date DATE,
# url varchar(32),
# url_ID varchar (32),
# PRIMARY KEY (url_ID));


class NewsHunt:
    def scrape(self):
        conn = MySQLdb.connect(host='127.0.0.1', user='root',
                               password='password', db='bbc')
        with conn.cursor() as cur:
            sql_fetch = """
            SELECT url_ID FROM test.africa
            """
            cur.execute(sql_fetch)

            ids_stored = [i[0] for i in cur.fetchall()]
            res = requests.get('https://www.bbc.com')
            print(res.raise_for_status())

            # to store response as html file
            soup = bs4.BeautifulSoup(res.text, 'html.parser')
            linkElems = soup.select('.media__link')
            todays_catch = {'publish_date': [], 'url': [], 'url_ID': []}

            for i in range(len(linkElems)):
                # we check whether this article was viewed and stored already
                if ('Africa'.lower() in linkElems[i].get('href') and
                        int(linkElems[i].get('href')[-8:]) not in ids_stored):
                    urlToOpen = 'https://www.bbc.com' + \
                        linkElems[i].get('href')
                    # opens related web articles in your browser - if not yet seen
                    webbrowser.open(urlToOpen)
                    todays_catch['publish_date'].append(today_date)
                    todays_catch['url'].append(urlToOpen)
                    todays_catch['url_ID'].append(urlToOpen[-8:])

            headers = [k for k in todays_catch.keys()]
            data = tuple(zip(todays_catch[headers[0]],

                             todays_catch[headers[1]], todays_catch[headers[2]]))

            placeholders = len(headers)*['%s']
            sql_insert_template = """
            INSERT INTO bbc.africa ({headers}) VALUES({placeholders})
            """
            sql = sql_insert_template.format(headers=', '.join(headers),
                                             placeholders=','.join(placeholders))
            cur.executemany(sql, data)

        conn.commit()
        conn.close()

        print(
            f'Today {len(todays_catch[headers[0]])} article got loaded into database.')


news = NewsHunt()
news.scrape()
