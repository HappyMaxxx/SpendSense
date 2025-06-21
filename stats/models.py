from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import json

class WeekAmount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    data = models.TextField()
    last_update = models.DateTimeField(auto_now_add=True)
    times_update = models.IntegerField(default=0)

    def set_data(self, value):
        self.data = json.dumps(value)

    def get_data(self):
        return json.loads(self.data)
    
    def update_data(self, func):
        now = timezone.now()
        start_of_this_week = now - timedelta(days=now.weekday())

        if self.last_update < start_of_this_week:
            new_data = func(self.user)

            try:
                existing_data = self.get_data()
            except json.JSONDecodeError:
                existing_data = [0] * 7

            if len(existing_data) != 7:
                existing_data = [0] * 7

            updated_data = []
            for old, new in zip(existing_data, new_data):
                avg = (old * self.times_update + new) / (self.times_update + 1)
                updated_data.append(round(avg, 2)) 

            self.set_data(updated_data)
            self.last_update = now
            self.times_update += 1
            self.save()