from datetime import date

from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.db import models


class Client(models.Model):

    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    patronymic = models.CharField(max_length=30)
    gender = models.SmallIntegerField(default=0)

    born_date = models.DateField(blank=True)
    avatar = models.ImageField(upload_to="avatar/", blank=True)

    address = models.CharField(max_length=255, blank=True, null=True,)
    is_online = models.BooleanField(default=False)

    phone = models.CharField(
        max_length=32,
        verbose_name=_('Phone'),
        blank=True,
    )

    email = models.EmailField(
        verbose_name=_('Email'),
        blank=True,
    )

    passport = models.CharField(
        max_length=20,
        verbose_name=_('Passport'),
        blank=True,
    )
    note = models.CharField(max_length=100, blank=True, null=True)
    manager = models.ForeignKey(settings.AUTH_USER_MODEL)

    class Meta:
        unique_together = (
            'first_name', 'last_name', 'patronymic', 'born_date')

    def save(self, *args, **kwargs):
        self.first_name = self.first_name.upper()
        self.last_name = self.last_name.upper()
        self.patronymic = self.patronymic.upper()
        super(Client, self).save(*args, **kwargs)

    def __unicode__(self):
        return unicode(self.get_full_name())

    def get_full_name(self):
        return unicode('%s %s' % (self.first_name, self.last_name))

    def initials(self):
        return unicode('%s %s. %s.' %
                       (self.last_name, self.first_name[
                        0], self.patronymic[0],)
                       )

    def initialsC(self):
        return unicode('%s%s %s%s %s%s' %
                       (self.last_name[0], self.last_name[1:].lower(),
                        self.first_name[0], self.first_name[1:].lower(),
                        self.patronymic[0], self.patronymic[1:].lower(),
                        )
                       )

    def full_nameC(self):
        return unicode('%s%s %s. %s.' %
                       (self.last_name[0], self.last_name[
                        1:].lower(), self.first_name[0], self.patronymic[0],)
                       )

    def age(self):
        today = date.today()
        try:
            birthday = self.born_date.replace(year=today.year)
        except ValueError:
            # raised when birth date is February 29 and the current year is not
            # a leap year
            birthday = self.born_date.replace(
                year=today.year, month=self.born_date.month+1, day=1)

        if birthday > today:
            return today.year - self.born_date.year - 1
        else:
            return today.year - self.born_date.year

    def as_json(self):
        return dict(id=self.id, first_name=self.first_name,
                    last_name=self.last_name, patronymic=self.patronymic,
                    born_date=self.born_date.strftime("%m/%d/%Y"),
                    phone=self.phone, gender=self.gender,
                    address=self.address, email=self.email,
                    passport=self.passport,)

    @property
    def is_active(self):
        return self.contract_set.filter(is_current=1).exists()
