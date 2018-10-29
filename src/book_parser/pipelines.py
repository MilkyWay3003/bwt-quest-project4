# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
import datetime
import logging
import pprint
import smtplib

from book_parser import settings
from book_parser.items import BookParserItem
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from scrapy.mail import MailSender


class MySQLPipeline(object):
    def __init__(self):
        self.connect = pymysql.connect(
            host=settings.MYSQL_HOST,
            db=settings.MYSQL_DBNAME,
            user=settings.MYSQL_USER,
            passwd=settings.MYSQL_PASSWD,
            charset='utf8',
            use_unicode=True)
        self.cursor = self.connect.cursor()

    def process_item(self, item, spider):
        if item.__class__ == BookParserItem:
            try:
                table_name = 'books'
                sql = "insert into %s (genre, title, description, price, rating," \
                      "upc, product_type, price_excl_tax, price_incl_tax, tax, " \
                      "availability, num_reviews, image_urls) " \
                      "values ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s', '%s')"

                data = (table_name, item['genre'], self.connect.escape_string(item['title']),
                        self.connect.escape_string(item['description']), item['price'], item['rating'], item['upc'],
                        item['product_type'], item['price_excl_tax'], item['price_incl_tax'], item['tax'],
                        item['availability'], item['num_reviews'], 'images/' + item['images'][0]['path'])

                self.cursor.execute(sql % data)
                self.connect.commit()

            except Exception as error:
                logging.log(error)
            return item

    def close_spider(self, spider):
        self.connect.close()

        gmail_user = 'natali.myronova@gmail.com'
        gmail_password = '1234'
        recipient = 'natali.myronova@gmail.com'

        msg = MIMEMultipart()
        msg['From'] = gmail_user
        msg['To'] = recipient
        mail_subject = 'Book Scraper Report for ' + datetime.date.today().strftime("%m/%d/%y")
        msg['Subject'] = mail_subject

        intro = "Summary stats from Scrapy BooksSpider: \n\n"
        body = spider.crawler.stats.get_stats()
        body = pprint.pformat(body)
        body = intro + body
        msg.attach(MIMEText(body, 'plain'))

        mail_server = smtplib.SMTP('smtp.gmail.com', 587)
        mail_server.ehlo()
        mail_server.starttls()
        mail_server.ehlo()
        mail_server.login(gmail_user, gmail_password)
        mail_server.sendmail(gmail_user, recipient, msg.as_string())
        mail_server.close()

        mail_sender = MailSender(mailfrom=gmail_user, smtphost="smtp.gmail.com", smtpport=587,
                                 smtpuser=gmail_user, smtppass=gmail_password)
        mail_sender.send(to=[gmail_user], subject=mail_subject, body=msg.as_string(), cc=None)


