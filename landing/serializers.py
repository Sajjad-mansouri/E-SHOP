from rest_framework import serializers

from landing.models import EmailInbox


class EmailInboxSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailInbox
        fields = ["name", "email", "message", "subject"]
