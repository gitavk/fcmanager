from django.contrib.auth.models import AbstractUser
from datetime import datetime

from organizer.models import Note, NoteUsers
from reception.models import Reminder


class User(AbstractUser):
    """
    Users within the Django authentication system are represented by this
    model.

    Username, password and email are required. Other fields are optional.
    """
    def __str__(self):
        return self.get_full_name()

    class Meta(AbstractUser.Meta):
        swappable = 'CORE_USER_MODEL'

    def initials(self):
        return unicode(
            '%s%s %s.' %
            (self.last_name[0], self.last_name[1:].lower(), self.first_name[0])
        )

    def initialsC(self):
        if self.last_name and self.first_name:
            return unicode(
                '%s%s %s%s' %
                (
                    self.last_name[0],
                    self.last_name[1:].lower(),
                    self.first_name[0],
                    self.first_name[1:].lower(),
                )
            )
        elif self.last_name:
            return unicode(
                '%s%s %s%s' %
                (self.last_name[0], self.last_name[1:].lower())
            )
        else:
            return ''

    def has_msg(self):
        td = datetime.now().date()
        need_read = NoteUsers.objects.filter(is_read=0, user=self).values('note')
        return Note.objects.filter(pk__in=need_read, datetodo__lte=td).count()

    def msg(self):
        need_read = NoteUsers.objects.filter(is_read=0, user=self).values('note')
        return Note.objects.filter(pk__in=need_read,)

    def is_manager(self):
        return self.groups.all().filter(name='manager').count()

    def is_reception(self):
        return self.groups.all().filter(name='reception').count()

    def reminders(self):
        reminders = Reminder.objects.filter(
            is_read=False, is_everyday=True, time__lte=datetime.now().time()
        )
        reminders = reminders | Reminder.objects.filter(
            is_read=False,
            date__lte=datetime.now().date(),
            time__lte=datetime.now().time()
        )

        wday = datetime.now().weekday()

        for r in Reminder.objects.filter(
            is_read=False, is_everyday=False, date__isnull=True
        ):
            if wday in [int(x) for x in r.wdays[:-1].split(',')]:
                reminders = reminders | Reminder.objects.filter(pk=r.pk)

        return reminders
