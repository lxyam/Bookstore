import jwt
import time
import logging
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from be.model import error
from be.model import db_conn

# encode a json string like:
#   {
#       "user_id": [user name],
#       "terminal": [terminal code],
#       "timestamp": [ts]} to a JWT
#   }


def jwt_encode(user_id: str, terminal: str) -> str:
    encoded = jwt.encode(
        {"user_id": user_id, "terminal": terminal, "timestamp": time.time()},
        key=user_id,
        algorithm="HS256",
    )
    return encoded.encode("utf-8").decode("utf-8")


# decode a JWT to a json string like:
#   {
#       "user_id": [user name],
#       "terminal": [terminal code],
#       "timestamp": [ts]} to a JWT
#   }
def jwt_decode(encoded_token, user_id: str) -> str:
    decoded = jwt.decode(encoded_token, key=user_id, algorithms="HS256")
    return decoded


class User():
    token_lifetime: int = 3600  # 3600 second

    def __init__(self):
        db_conn.__init__(self)

    def __check_token(self, user_id, db_token, token):
        try:
            if db_token != token:
                return False
            jwt_text = jwt_decode(encoded_token=token, user_id=user_id)
            ts = jwt_text["timestamp"]
            if ts is not None:
                now = time.time()
                if self.token_lifetime > now - ts >= 0:
                    return True
        except jwt.exceptions.InvalidSignatureError as e:
            logging.error(str(e))
            return False

    def register(self, user_id: str, password: str):
        token = ""
        try:
            terminal = "terminal_{}".format(str(time.time()))
            token = jwt_encode(user_id, terminal)
            self.session.execute(  
                "INSERT INTO user (user_id, password, balance, token, terminal) values (:user_id, :password, 0, :token, :terminal)",
                {"user_id":user_id,"password": password,"token":token,"terminal":terminal })
            self.session.commit()
        except sqlalchemy.exc.IntegrityError:
            return error.error_exist_user_id(user_id)
        return 200, "ok"


    def unregister(self, user_id: str, password: str):
        user = self.session.execute("SELECT password from user where user_id=:user_id",{"user_id": user_id}).fetchone()
        if user == None:
            code, message = error.error_authorization_fail()
            return code, message
        if password != user.password:
            code, message = error.error_authorization_fail()
            return code, message
        self.session.execute("DELETE from user where user_id='%s'" % (user_id,))
        self.session.commit()
        return 200, "ok"

    def check_token(self, user_id: str, token: str):
        cursor = self.session.execute("SELECT token from user where user_id=?", (user_id,))
        if cursor.fetchone() is None:
            return error.error_authorization_fail()
        row = cursor.fetchone()
        if not self.__check_token(user_id, row[0], token):
            return error.error_authorization_fail()
        return 200, "ok"

    def check_password(self, user_id: str, password: str):
        cursor = self.session.execute("SELECT password from user where user_id=?", (user_id,))
        if cursor.fetchone() is None:
            return error.error_authorization_fail()
        row = cursor.fetchone()
        if password != row[0]:
            return error.error_authorization_fail()
        return 200, "ok"

    def login(self, user_id: str, password: str, terminal: str):
        token = ""
        user = self.session.execute("SELECT password from user where user_id=:user_id",{"user_id":user_id}).fetchone()
        if user is None or password != user.password:
            code, message=error.error_authorization_fail()
            return code, message,token
        token = jwt_encode(user_id, terminal)
        self.session.execute(
            "UPDATE user set token= '%s', terminal = '%s' where user_id = '%s'"% (token, terminal, user_id) )
        self.session.commit()
        return 200, "ok", token

    def logout(self, user_id: str, token: str):
        try:
            user = self.session.execute("SELECT token from user where user_id='%s'" % (user_id)).fetchone()
            if user is None:
                return error.error_authorization_fail()
            if user.token != token:
                return error.error_authorization_fail()
            self.session.execute(
                "UPDATE user SET token = '%s' WHERE user_id='%s'" % ("", user_id))
            self.session.commit()
            return 200, "ok"
        except sqlalchemy.exc.IntegrityError:
            return error.error_authorization_fail()

    def change_password(self, user_id: str, old_password: str, new_password: str):
        user = self.session.execute("SELECT password from user where user_id='%s'"%(user_id,)).fetchone()
        if user is None  or old_password != user.password:
            return error.error_authorization_fail()
        self.session.execute(
            "UPDATE user set password = '%s' where user_id = '%s'"%(new_password, user_id),)
        self.session.commit()
        return 200, "ok"

