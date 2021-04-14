from django.contrib.auth.models import User
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db import models
from django.db.models import signals as dbsignals
from django.dispatch import receiver
from uuslug import uuslug


class MozillianProfile(models.Model):
    """Mozillians User Profile"""

    user = models.OneToOneField(
        User, related_name="userprofile", on_delete=models.CASCADE
    )
    slug = models.SlugField(blank=True, max_length=100)
    username = models.CharField(max_length=40)
    avatar_url = models.URLField(max_length=400, default="", blank=True)
    is_nda_member = models.BooleanField(default=False)

    def __str__(self):
        return self.username

    class Meta:
        ordering = ["username"]

    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = uuslug(self.username, instance=self)
        super(MozillianProfile, self).save(*args, **kwargs)

    @property
    def is_admin(self):
        return self.user.groups.filter(name="Admin").exists() or self.user.is_superuser


@receiver(dbsignals.post_save, sender=User, dispatch_uid="create_user_profile_sig")
def create_user_profile(sender, instance, created, raw, **kwargs):
    if not raw:
        up, created = MozillianProfile.objects.get_or_create(user=instance)
        if not created:
            dbsignals.post_save.send(
                sender=MozillianProfile, instance=up, created=created, raw=raw
            )


class Event(models.Model):
    """Event model."""

    name = models.CharField(max_length=400)
    archived = models.BooleanField(default=False)
    slug = models.SlugField(max_length=400, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_nda = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = uuslug(self.name, instance=self)
        super(Event, self).save(*args, **kwargs)

    @property
    def questions_count(self):
        return self.questions.all().count()


class Question(models.Model):
    """Question relational model."""

    asked_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    event = models.ForeignKey(Event, related_name="questions", on_delete=models.CASCADE)
    question = models.TextField(
        validators=[MaxLengthValidator(280), MinLengthValidator(10)]
    )
    answer = models.TextField(
        validators=[MaxLengthValidator(280)], default="", blank=True
    )
    addressed = models.BooleanField(default=False)
    is_anonymous = models.BooleanField(default=False, blank=False)

    def __str__(self):
        return "Question {pk} from {user}".format(pk=self.id, user=self.asked_by)


class Vote(models.Model):
    """Vote model."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(
        Question, related_name="votes", on_delete=models.CASCADE
    )
    date_voted = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "question")

    def __str__(self):
        return "Vote of {user} for {question}".format(
            user=self.user, question=self.question
        )
