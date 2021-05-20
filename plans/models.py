from django.db import models
from django.contrib.auth.models import User


class MiningPlan(models.Model):
    title = models.CharField(max_length=255)
    text = models.TextField()
    premium = models.BooleanField(default=True)


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    stripeid = models.CharField(max_length=255)
    stripe_subscription_id = models.CharField(max_length=255)
    cancel_at_period_end = models.BooleanField(default=False)
    membership = models.BooleanField(default=False)
    user_balance = models.FloatField(default=0.00)


class Bets(models.Model):
    title = models.CharField(max_length=100)
    home = models.CharField(max_length=100)
    away = models.CharField(max_length=100)
    home_odds = models.FloatField(default=1.00)
    away_odds = models.FloatField(default=1.00)
    draw_odds = models.FloatField(default=1.00)
