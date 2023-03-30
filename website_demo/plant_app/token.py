# email verification
# https://codertw.com/%E7%A8%8B%E5%BC%8F%E8%AA%9E%E8%A8%80/369030/
from itsdangerous import URLSafeSerializer as utsr

class Token():
    def __init__(self):
        self.security_key = "it_is_secret"
        self.salt = "activate user"

    def generate_validate_token(self, username):
        serializer = utsr(self.security_key)
        # 加密token
        return serializer.dumps(username, salt=self.salt)

    def confirm_validate_token(self, token, expiration=600):
        serializer = utsr(self.security_key)
        # 解密token
        return serializer.loads(token, salt=self.salt, max_age=expiration)