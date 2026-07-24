from django.db import models


class Visit(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    audience = models.CharField(max_length=20)
    path = models.CharField(max_length=200)

    class Meta:
        indexes = [models.Index(fields=["audience", "timestamp"])]


class OutboundClick(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    destination = models.CharField(max_length=50)
    audience = models.CharField(max_length=20)

    class Meta:
        indexes = [models.Index(fields=["destination", "audience"])]