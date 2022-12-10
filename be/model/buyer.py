import  jwt
from datetime import datetime
import json
import sqlalchemy
import logging
from be.model import db_conn
from be.model import error
import uuid
import time
from flask import jsonify


class Buyer():
    def __init__(self):
        db_conn.__init__(self)

    def new_order(self, user_id: str, store_id: str, id_and_count: [(str, int)]):
        try:
            order_id = ""
            user = self.session.execute("SELECT user_id FROM user WHERE user_id = '%s';" % (user_id,)).fetchone()
            if user is None:
                code, mes = error.error_non_exist_user_id(user_id)
                return code, mes, order_id
            store_info = self.session.execute("SELECT user_id FROM user_store WHERE store_id = '%s';" % (store_id,)).fetchone()
            if store_info is None:
                code, mes = error.error_non_exist_store_id(store_id)
                return code, mes, order_id
            order_id = user_id  + str(uuid.uuid1())
            list_ = []
            for book_id, cnt in id_and_count:
                book_id=int(book_id)
                book = self.session.execute("SELECT stock_level, price FROM store WHERE store_id = '%s' AND book_id = %d" % (store_id, book_id)).fetchone()
                if book is None:
                    code, mes = error.error_non_exist_book_id(str(book_id))
                    return code, mes, " "
                elif book[0] < cnt:
                    code, mes = error.error_stock_level_low(str(book_id))
                    return code, mes, " "
                else:
                    list_.append([book_id, cnt, book[1]])
            sum = 0
            for book_id, cnt, price in list_:
                sum = sum + cnt * price
                res = self.session.execute("UPDATE store set stock_level = stock_level - %d WHERE store_id = '%s' and book_id = %d  and stock_level >=%d" % (count, store_id, book_id, count))
                if res.rowcount == 0:
                    code, mes = error.error_stock_level_low(book_id)
                    return code, mes, " "
                self.session.execute("INSERT INTO new_order_detail(order_id, book_id, count, price) VALUES('%s',%d, %d, %d);" % (order_id, book_id, count, price))
            _time = datetime.utcnow()
            self.session.execute("INSERT INTO new_order_pend(order_id, buyer_id,store_id,price,pt) VALUES('%s', '%s','%s',%d,:_time);" % (order_id, user_id, store_id, sum),{'_time':datetime.utcnow()})
            overtime_append(datetime.utcnow().second,order_id)
            self.session.commit()
            return 200, "ok", order_id

        except sqlalchemy.exc.IntegrityError:
            code, mes = error.error_duplicate_bookid()
            return code, mes, " "

        except ValueError:
            code, mes = error.error_non_exist_book_id(book_id)
            return code, mes, " "



    def payment(self, buyer_id, password, order_id):
        try:
            result = self.session.execute(
                "SELECT buyer_id, price, store_id FROM new_order_pend WHERE order_id = '%s'" % (order_id,)).fetchone()
            if result is None:
                return error.error_invalid_order_id(order_id)
            elif result[0] != buyer_id:
                return error.error_authorization_fail()
            result = self.session.execute("SELECT balance, password FROM user WHERE user_id = '%s';" % (buyer_id)).fetchone()
            if result is None:
                return error.error_non_exist_user_id(buyer_id)
            elif result[0] < result[1]:
                error.error_not_sufficient_funds(order_id)
            elif result[1] != password:
                return error.error_authorization_fail()
            result = self.session.execute("UPDATE user set balance = balance - %d WHERE user_id = '%s' AND balance >= %d" % (result[1], buyer_id, result[1]))
            if result.rowcount == 0:
                return error.error_not_sufficient_funds(order_id)
            store_info = self.session.execute("SELECT user_id FROM user_store WHERE store_id = '%s';" % (result[2],)).fetchone()
            result = self.session.execute("UPDATE usr set balance = balance + %d WHERE user_id = '%s'" % (result[1], store_info[0]))
            if result.rowcount == 0:
                return error.error_non_exist_user_id(buyer_id)
            result = self.session.execute("DELETE FROM new_order_pend WHERE order_id = '%s'" % (order_id,))
            if result.rowcount == 0:
                return error.error_invalid_order_id(order_id)
            _time = datetime.utcnow()
            self.session.execute("INSERT INTO new_order_paid(order_id, buyer_id,store_id,price,status, pt) VALUES('%s', '%s','%s',%d,'%s',:_time);" % (order_id, buyer_id, result[2], result[1], 0),{'_time':_time})
            self.session.commit()

        except BaseException:
            return 530, "{}".format(str(BaseException))
        return 200, "ok"


    def add_funds(self, user_id, password, add_value):
        try:
            usr = self.session.execute("SELECT password from user where user_id='%s'" % (user_id,)).fetchone()
            if usr is None:
                return error.error_non_exist_user_id(user_id)
            elif password != usr.password:
                return error.error_authorization_fail()
            self.session.execute("UPDATE user SET balance = balance + %d WHERE user_id = '%s'"%(add_value, user_id))
            self.session.commit()
        except BaseException:
            return 530, "{}".format(str(BaseException))
        return 200, "ok"

    def receive_books(self, buyer_id, order_id):
        result = self.session.execute(
            "SELECT status, buyer_id FROM new_order_paid WHERE order_id = '%s'" % (order_id,)).fetchone()
        if result is None:
            return error.error_invalid_order_id(order_id)
        elif result[0] == 0:
            return 522, " The book has not been sent to customer yet"
        elif result[0] == 2:
            return 523, "The book has been received by customer"
        elif result[1] != buyer_id:
            return error.error_authorization_fail()
        self.session.execute("UPDATE new_order_paid set status=2 where order_id = '%s' ;" % (order_id))
        self.session.commit()
        return 200, "ok"

    def search_order(self, buyer_id):
        user = self.session.execute("SELECT user_id FROM usr WHERE user_id = '%s';" % (user_id,)).fetchone()
        if user is None:
            code, mes = error.error_non_exist_user_id(buyer_id)
            return code, mes, " "
        ret = []
        result = self.session.execute("SELECT new_order_detail.order_id,title,new_order_detail.price,count,status,pt,new_order_paid.price \
            FROM new_order_paid,new_order_detail,book WHERE book.book_id=new_order_detail.book_id and \
            new_order_paid.order_id=new_order_detail.order_id and new_order_paid.buyer_id = '%s' order by new_order_detail.order_id" % (buyer_id)).fetchall()
        if len(result) != 0:
            order_id = result[0][0]
            details=[]
            status_map = ['not shipped', 'shipped', 'received']
            for i in range(len(result)):
                record = result[i]
                if record[0] == order_id :
                    details.append({'title':record[1],'price':record[2],'count':record[3]})
                else:
                    status=result[i-1][4]
                    ret.append({'order_id':order_id,'status':status_map[status],'time':json.dumps(records[i-1][5],cls=DateEncoder),'total_price':records[i-1][6],'detail':details})
                    details = []
                    details.append({'title': record[1], 'price': record[2], 'count': record[3]})
                order_id = record[0]
            status= result[-1][4]
            ret.append({'order_id': order_id, 'status': status_map[status], 'time': json.dumps(records[- 1][5],cls=DateEncoder),'total_price':records[i-1][6], 'detail': details})
        result = self.session.execute("SELECT new_order_detail.order_id,title,new_order_detail.price,count,pt,new_order_pend.price "
            "FROM new_order_pend,new_order_detail,book WHERE book.book_id=new_order_detail.book_id and "
            "new_order_pend.order_id=new_order_detail.order_id and buyer_id = '%s'" % (buyer_id)).fetchall()
        if len(result)!=0:
            order_id = result[0][0]
            details=[]
            for i in range(len(result)):
                record=result[i]
                if record[0] == order_id :
                    details.append({'title':record[1],'price':record[2],'count':record[3]})
                else:
                    ret.append({'order_id':order_id,'status':'not paid','time':json.dumps(result[i-1][4],cls=DateEncoder), 'total_price':result[i-1][5], 'detail':details})
                    details = []
                    details.append({'title': record[1], 'price': record[2], 'count': record[3]})
                order_id = record[0]
            ret.append({'order_id': order_id, 'status':'not paid', 'time': json.dumps(result[- 1][4],cls=DateEncoder),'total_price':result[i-1][5],'detail': details})
        if len(ret) != 0:
            return 200, 'ok', ret
        else:
            return 200, 'ok', "0"


    def cancel(self, buyer_id, order_id):
        if not self.check_user(buyer_id):
            code, mes = error.error_non_exist_user_id(buyer_id)
            return code, mes
        store = self.session.execute("Select store_id,price FROM new_order_pend WHERE order_id = '%s' and buyer_id='%s'" % (order_id, buyer_id)).fetchone()
        if store is not None:
            store_id, price = store[0], store[1]
            result = self.session.execute("DELETE FROM new_order_pend WHERE order_id = '%s'" % (order_id,))
        else:
            info = self.session.execute("Select store_id,price FROM new_order_paid WHERE order_id = '%s' and buyer_id='%s' and status='0'" % (order_id,buyer_id)).fetchone()
            if info is not None:
                store_id, price = info[0], info[1]
                self.session.execute("DELETE FROM new_order_paid WHERE order_id = '%s' and status='0'" % (order_id,))
                user_id = self.session.execute("SELECT user_id FROM user_store WHERE store_id = '%s';" % (info[0],)).fetchone()
                self.session.execute("UPDATE usr set balance = balance - %d WHERE user_id = '%s'" % (info[1], user_id[0]))
                self.session.execute("UPDATE usr set balance = balance + %d WHERE user_id = '%s'" % (info[1], buyer_id))
            else:
                return error.error_invalid_order_id(order_id)
        self.session.execute("INSERT INTO new_order_cancel(order_id, buyer_id,store_id,price,pt) VALUES('%s', '%s','%s',%d,:_time);" % (order_id, buyer_id, store_id, price), {'_time': datetime.utcnow()})
        self.session.execute("Update store Set stock_level = stock_level +  count from new_order_detail Where new_order_detail.book_id = store.book_id and store.store_id = '%s' and new_order_detail.order_id = '%s'" % (store_id,order_id))
        self.session.commit()
        return 200, 'ok'


