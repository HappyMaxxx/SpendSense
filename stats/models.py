from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
import json

class WeekAmount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    data = models.TextField()
    last_update = models.DateTimeField(auto_now_add=True)
    times_update = models.IntegerField(default=0)

    def set_data(self, value):
        self.data = json.dumps(value)
        self.save()

    def get_data(self):
        if self.data:
            return json.loads(self.data)
        return [0] * 7
    
    def update_data(self, func):
        now = timezone.now().date()
        start_of_this_week = now - timedelta(days=now.weekday())
        start_of_last_week = start_of_this_week - timedelta(days=7)
        end_of_last_week = start_of_this_week - timedelta(seconds=1)

        last_update_date = self.last_update.date() if self.last_update else None

        if last_update_date is None or last_update_date < start_of_this_week:
            new_data = func(self.user, start_of_last_week, end_of_last_week)

            try:
                existing_data = self.get_data()
            except json.JSONDecodeError:
                existing_data = [0] * 7

            updated_data = []
            for old, new in zip(existing_data, new_data):
                avg = (old * self.times_update + new) / (self.times_update + 1)
                updated_data.append(int(avg))

            self.set_data(updated_data)
            self.last_update = timezone.now()
            self.times_update += 1
            self.save()
            
            return True
        return False