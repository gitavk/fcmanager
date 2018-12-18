from datetime import datetime, date

from django.db import models
from django.conf import settings


class Guest(models.Model):
    id = models.AutoField(primary_key=True)
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='g_manager')
    date = models.DateField()
    firstname = models.CharField(max_length=30)
    lastname = models.CharField(max_length=30)
    patronymic = models.CharField(max_length=30)
    born = models.DateField()
    phone = models.CharField(max_length=32)
    avatar = models.ImageField(upload_to="avatar/", blank=True)
    is_client = models.SmallIntegerField(default=0)

    class Meta:
        unique_together = ('firstname', 'lastname', 'patronymic', 'born')

    def __unicode__(self):
        return unicode('%s %s' % (self.lastname, self.firstname))

    def get_full_name(self):
        return unicode('%s %s' % (self.firstname, self.lastname))

    def initials(self):
        return unicode(
            '%s %s. %s.' %
            (self.lastname, self.firstname[0], self.patronymic[0],)
        )

    def save(self, *args, **kwargs):
        self.firstname = self.firstname.upper()
        self.lastname = self.lastname.upper()
        self.patronymic = self.patronymic.upper()
        super(Guest, self).save(*args, **kwargs)

    def age(self):
        today = date.today()
        try:
            birthday = self.born.replace(year=today.year)
        except ValueError:
            # raised when birth date is February 29 and the current year is not a leap year
            birthday = self.born.replace(year=today.year, month=self.born.month + 1, day=1)

        if birthday > today:
            return today.year - self.born.year - 1
        else:
            return today.year - self.born.year

    # for compatible with person.models
    def last_name(self):
        return self.lastname

    def first_name(self):
        return self.firstname

    def born_date(self):
        return self.born


class Reminder(models.Model):
    id = models.AutoField(primary_key=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL)
    text = models.CharField(max_length=150)
    time = models.TimeField()
    is_everyday = models.BooleanField(default=True)
    date = models.DateField(blank=True, null=True)
    wdays = models.CharField(max_length=14, blank=True, null=True)
    is_read = models.BooleanField(default=False)

    def read(self, user):
        ReadBy(user=user, reminder=self).save()
        self.is_read = True
        self.save()


class ReadBy(models.Model):
    id = models.AutoField(primary_key=True)
    readtime = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, )
    reminder = models.ForeignKey(Reminder)


class GuestVisits(models.Model):
    id = models.AutoField(primary_key=True)
    date_start = models.DateTimeField()
    date_end = models.DateTimeField(blank=True, null=True)
    locker = models.IntegerField()
    guest = models.ForeignKey(Guest)
    is_online = models.IntegerField(default=-1)

    def out(self):
        self.date_end = datetime.now()
        self.is_online = self.id
        self.save()

    class Meta:
        unique_together = ("guest", "is_online")
