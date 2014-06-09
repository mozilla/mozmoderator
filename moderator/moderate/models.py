from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxLengthValidator, MinLengthValidator

from uuslug import uuslug


class Event(models.Model):
    """Event model."""
    name = models.CharField(max_length=400)
    archived = models.BooleanField(default=False)
    slug = models.SlugField(max_length=400)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = uuslug(self.name, instance=self)
        super(Event, self).save(*args, **kwargs)

    @property
    def questions_count(self):
        return self.questions.all().count()


class MozillianProfile(models.Model):
    """Mozillians User Profile"""
    user = models.OneToOneField(User, related_name='userprofile')
    slug = models.SlugField(blank=True, max_length=100)
    username = models.CharField(max_length=40)
    avatar_url = models.URLField(max_length=400, default='')

    def __unicode__(self):
        return self.username

    class Meta:
        ordering = ['username']

    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = uuslug(self.username, instance=self)
        super(MozillianProfile, self).save(*args, **kwargs)


class Question(models.Model):
    """Question relational model."""
    asked_by = models.ForeignKey(User)
    event = models.ForeignKey(Event, related_name='questions')
    question = models.TextField(validators=[MaxLengthValidator(140),
                                            MinLengthValidator(10)])


class Vote(models.Model):
    """Vote model."""
    user = models.ForeignKey(User)
    question = models.ForeignKey(Question, related_name='votes')
    date_voted = models.DateField(auto_now_add=True)
