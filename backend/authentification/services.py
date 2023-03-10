from argon2 import PasswordHasher,exceptions
from flask_mail  import Message
from backend import mail
from backend.authentification.errors import UserNotFoundError,VerificationError
from backend.database.database import FindUser,CreateUser,GenerateVerificationToken
from flask import current_app
import re
ph = PasswordHasher()

def register_user(username,email,password,):
    user = FindUser(email)
    if user:
        raise Exception({"message": "Email already used", "code": 409})
    pattern = re.compile("^[ a-zA-Z0-9!@#$%^&*()_+\-=\[\\]'\"{};:,.<>\/?]+$")
    if not pattern.match(password):
        raise Exception({"message": "Password contains forbidden characters", "code": 400})

    hashed_password = hash_password(password)
    user=CreateUser(username,email,hashed_password)
    generate_email_validation_token(user)

def generate_email_validation_token(user):
    if user.validated:
        raise Exception({"message": "Email already validated", "code": 409})
    token = GenerateVerificationToken(user)
    send__confirmation_email(user.username,user.email,token)


def hash_password(password):
    hash = ph.hash(password)
    try:
      ph.verify(hash, password)
    except: raise
    return hash

def login(email, password):
    user = FindUser(email)
    if user is None:
        raise UserNotFoundError("User not found")

    hash = user.password
    try:
        ph.verify(hash, password)
    except exceptions.VerifyMismatchError as e:
        print(type(e))
        raise VerificationError("Incorrect password")
    return user
    # if ph.check_needs_rehash(hash):
    #      db.set_password_hash_for_user(user, ph.hash(password))

def send__confirmation_email(username,email,token):
    print(token)
    msg = Message(sender=current_app.config["MAIL_DEFAULT_SENDER"],recipients = [email])
    msg.subject = "Confirmation email"
    msg.body = f"""Please Confirm Your Password Using This Link :
                    Link {token}"""
    mail.send(msg)
    # return  make_response("Email Successfully Sent",200)
    # except Exception as  error:
    #     return make_response(str(error),400)