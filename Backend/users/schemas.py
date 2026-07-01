from ninja import Schema

class RegisterSchema(Schema):
    username:   str = ""
    email:      str
    password:   str
    first_name: str = ""
    last_name:  str = ""
    telephone:  str = ""
    role:       str = "CLIENT"

class LoginSchema(Schema):
    email: str
    password: str

class MFAVerifySchema(Schema):
    email: str
    code: str

class UserOutSchema(Schema):
    id:         int
    username:   str
    email:      str
    role:       str
    telephone:  str
    first_name: str
    last_name:  str
    is_active:  bool