from django.contrib.auth.backends import ModelBackend
from .models import User

class EmailBackend(ModelBackend):   # 🔥 NAME EXACT same

    def authenticate(self, request, username=None, password=None, **kwargs):
        email = kwargs.get('email') or username

        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

        return None