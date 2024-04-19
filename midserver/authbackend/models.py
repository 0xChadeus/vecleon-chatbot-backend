from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
# from django.contrib.auth import get_user_model
# from django.contrib.auth.backends import ModelBackend


# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, email, password):
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user 

    def create_superuser(self, email, password):
        user = self.create_user(
            email,
            password,
        )
        user.is_staff = True
        user.subscription_is_active = True
        user.subscription_package = "Unlimited"
        user.stripe_subscription_id = "admin"
        user.stripe_customer_id = "admin"
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
    )
    username = models.CharField(
        db_index=True, 
        max_length=255
    )
    is_staff = models.BooleanField(default=False)
    free_msgs = models.IntegerField(default=1000)
    stripe_customer_id = models.CharField(default="")
    stripe_subscription_id = models.CharField(default="")
    subscription_package = models.CharField(default="")
    subscription_is_active = models.BooleanField(default=False)
    subscription_is_cancelled = models.BooleanField(default=False)
    #legacy
    messages_left=models.IntegerField(default=0)
    #Current number of tokens used
    current_usage=models.IntegerField(default=0)
    input_tokens=models.IntegerField(default=0)
    output_tokens=models.IntegerField(default=0)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["password"]

    def __str__(self):
        return self.email
    
    def get_username(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        if self.is_staff:
            return True
        else:
            return False

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        if self.is_staff:
            return True
        else:
            return False

    @property
    def get_subscription_status(self):
        return self.subscription_is_active

