from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import ugettext_lazy as _
from requests_oauthlib import OAuth1Session
from django.conf import settings
from django.db import models

from .utils import CustomClient

class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

class User(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)
    # fields for Warwick OAuth
    user_id = models.IntegerField(null=True, unique=True)
    access_token = models.CharField(max_length=100, null=True)
    access_token_secret = models.CharField(max_length=100, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def get_oauth_session(self):
        """
        Return a OAuthSession to be used for requests to the Tabula API.
        """ 
        oauth = OAuth1Session(
            settings.CONSUMER_KEY, 
            settings.CONSUMER_SECRET,
            resource_owner_key=self.access_token,              
            resource_owner_secret=self.access_token_secret, 
            client_class=CustomClient
        )
        return oauth

class RequestTokenStore(models.Model):
    """
    Model to store authorized tokens returned from warwick OAuth API. Stores 
    both the oauth_token and oauth_token_secret. The oauth_token_secret is 
    retrived using the oauth_token as the key.
    """
    oauth_token = models.CharField(max_length=200)
    oauth_token_secret = models.CharField(max_length=200)

    @classmethod
    def get_secret(cls, token):
        """
        Return oauth_token_secret given an oauth_token or an empty string if no 
        match found.
        """
        secret = cls.objects.filter(oauth_token=token).order_by('id').first()
        
        if secret is None:
            return ''

        return secret.oauth_token_secret