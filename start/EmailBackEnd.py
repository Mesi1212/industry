from django.contrib.auth.backends import ModelBackend
from start.models import CustomUser

class EmailBackEnd(ModelBackend):
    def authenticate(self, username=None, password=None, **kwargs):
        try:
            user = CustomUser.objects.get(email=username)
        except CustomUser.DoesNotExist:
            print(f"User with email '{username}' does not exist")
            return None
        else:
            if user.check_password(password):
                print(f"User with email '{username}' authenticated successfully")
                return user
            else:
                print(f"Invalid password for user with email '{username}'")
        return None
