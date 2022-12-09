import  jwt
import time
import sqlalchemy
from be.model import db_conn
from be.model import error
import json

class Seller():
    def __init__(self):
        db_conn.__init__(self)

    def add_book(self, user_id: str, store_id: str, book_id: str, book_json_str: str, stock_level: int):
        try:
            user = self.session.execute("SELECT user_id FROM user WHERE user_id = '%s';"% (user_id,)).fetchone()
            if user is None:
                return error.error_non_exist_user_id(user_id)
            store = self.session.execute("SELECT store_id FROM user_store WHERE store_id = '%s';"% (store_id,)).fetchone()
            if store is None:
                 return error.error_non_exist_store_id(store_id)
            book_id = int(book_id)
            result = self.session.execute("SELECT book_id FROM book WHERE book_id = '%s';" % (book_id,)).fetchone()
            if result is None:
                book = json.loads(book_json_str)
                list_ = []
                for i in book.get('tags'):
                    if i.strip() != "":
                        list_ .append(i)
                book['tags'] = str(list_ )
                if book.get('picture') is not None:
                    self.session.execute(
                    "INSERT into book( book_id, title,author,publisher,original_title,translator,"
                    "pub_year,pages,original_price,currency_unit,binding,isbn,author_intro,book_intro,"
                    "content,tags,picture) VALUES ( :book_id, :title,:author,:publisher,:original_title,:translator,"
                    ":pub_year,:pages,:original_price,:currency_unit,:binding,:isbn,:author_intro,:book_intro,"
                    ":content,:tags,:picture)" , {'book_id':book['id'], 'title':book['title'],'author':book['author'],
                     'publisher':book['publisher'],'original_title':book['original_title'],'translator':book['translator'],
                    'pub_year':book['pub_year'],'pages':book['pages'],'original_price':book['price'],'currency_unit':book['currency_unit'],
                    'binding':book['binding'],'isbn':book['isbn'],'author_intro':book['author_intro'],'book_intro':book['book_intro'],
                     'content':book['content'],'tags':book['tags'],'picture':book['picture']})
                else:
                    self.session.execute(
                        "INSERT into book( book_id, title,author,publisher,original_title,translator,"
                        "pub_year,pages,original_price,currency_unit,binding,isbn,author_intro,book_intro,"
                        "content,tags) VALUES ( :book_id, :title,:author,:publisher,:original_title,:translator,"
                        ":pub_year,:pages,:original_price,:currency_unit,:binding,:isbn,:author_intro,:book_intro,"
                        ":content,:tags)",
                        {'book_id': book['id'], 'title': book['title'], 'author': book['author'],
                         'publisher': book['publisher'], 'original_title': book['original_title'],
                         'translator': book['translator'],
                         'pub_year': book['pub_year'], 'pages': book['pages'], 'original_price': book['price'],
                         'currency_unit': book['currency_unit'],
                         'binding': book['binding'], 'isbn': book['isbn'], 'author_intro': book['author_intro'],
                         'book_intro': book['book_intro'],
                         'content': book['content'], 'tags': book['tags']})

            self.session.execute("INSERT into store(store_id, book_id, stock_level,price) VALUES ('%s', %d,  %d,%d)"% (store_id, int(book_id), stock_level,price))
            self.session.commit()

        except sqlalchemy.exc.IntegrityError:
            return error.error_exist_book_id(str(book_id))
        return 200, "ok"

    def add_stock_level(self, user_id: str, store_id: str, book_id: str, add_stock_level: int):
        try:
            result = self.session.execute("SELECT user_id FROM user_store WHERE store_id = '%s';" % (store_id,)).fetchone()
            if result is None:
                return error.error_non_exist_store_id(store_id)
            if result.user_id != user_id:
                return error.error_non_exist_user_id(user_id)
            book_id = self.session.execute("SELECT book_id FROM store WHERE book_id = %d;"% (int(book_id),)).fetchone()
            if book_id is None:
                return error.error_non_exist_book_id(book_id)
            self.session.execute("UPDATE store SET stock_level = stock_level + %d "
                                 "WHERE store_id = '%s' AND book_id = %d" % (add_stock_level, store_id, int(book_id)))
            self.session.commit()
        except ValueError:
            code, mes = error.error_non_exist_book_id(book_id)
            return code, mes
        return 200, "ok"

    def create_store(self, user_id: str, store_id: str):
        try:
            user = self.session.execute("SELECT user_id FROM user WHERE user_id = '%s';"% (user_id,)).fetchone()
            if user is None:
                return error.error_non_exist_user_id(user_id)
            self.session.execute("INSERT into user_store(store_id, user_id) VALUES ('%s', '%s')" %(store_id, user_id))
            self.session.commit()
        except sqlalchemy.exc.IntegrityError:
            return error.error_exist_store_id(store_id)
        return 200, "ok"

    def send_books(self, seller_id, order_id):
        result = self.session.execute("SELECT status,store_id FROM new_order_paid  WHERE order_id = '%s'" % (order_id,)).fetchone()
        if result is None:
            return error.error_invalid_order_id(order_id)
        elif result[0] != 0:
            return 521, "books has already been sent to customers"
        else:
            result = self.session.execute("SELECT user_id FROM user_store WHERE store_id = '%s';" % (result[1],)).fetchone()
            if result[0] != seller_id:
                return error.error_authorization_fail()
            self.session.execute("UPDATE new_order_paid set status=1 where order_id = '%s' ;" % ( order_id))
            self.session.commit()
        return 200, "ok"
