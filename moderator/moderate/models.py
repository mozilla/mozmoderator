from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxLengthValidator, MinLengthValidator

from uuslug import uuslug


class Event(models.Model):
    """Event model."""
    name = models.CharField(max_length=400)
    slug = models.SlugField(max_length=400)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = uuslug(self.name, instance=self)
        super(Event, self).save(*args, **kwargs)


class MozillianProfile(models.Model):
    """Mozillians User Profile"""
    user = models.OneToOneField(User, related_name='userprofile')
    slug = models.SlugField(blank=True, max_length=100)
    full_name = models.CharField(max_length=255)
    city = models.CharField(max_length=50, default='', blank=True)
    country = models.CharField(max_length=50, default='')
    ircname = models.CharField(max_length=50, default='')
    avatar_url = models.URLField(max_length=400, default='')
    bio = models.TextField(default='', blank=True)

    def __unicode__(self):
        return self.full_name

    class Meta:
        ordering = ['full_name']

    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = uuslug(self.full_name, instance=self)
        super(MozillianProfile, self).save(*args, **kwargs)


class Question(models.Model):
    """Question relational model."""
    asked_by = models.ForeignKey(User)
    event = models.ForeignKey(Event, related_name='questions')
    question = models.TextField(validators=[MaxLengthValidator(140),
                                            MinLengthValidator(10)])

    @property
    def get_vote_count(self):
        return self.vote_set.all().count()


class Vote(models.Model):
    """Vote model."""
    user = models.ForeignKey(User)
    question = models.ForeignKey(Question)
    date_voted = models.DateField(auto_now_add=True)
