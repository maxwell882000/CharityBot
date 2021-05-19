from django.db import models

class TelegramUser(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    username = models.CharField(max_length=100, blank=True, null=True)
    language = models.CharField(max_length=2)


class HelpRequest(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    description = models.CharField(max_length=1024)
    help_type = models.CharField(max_length=20)
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE)
    helper = models.ForeignKey(TelegramUser, on_delete=models.SET_NULL, blank=True, null=True, related_name='helped_requests')
    hidden = models.BooleanField(default=False)
    has_conflict = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        get_latest_by = 'created_at'
    
    def is_completted(self):
        return self.reaction and self.reaction.owner_reaction == HelpRequestReaction.Reactions.YES


class HelpRequestComplain(models.Model):
    text = models.CharField(max_length=500)
    user_from = models.ForeignKey(TelegramUser, on_delete=models.SET_NULL, blank=True, null=True)
    help_request = models.ForeignKey(HelpRequest, on_delete=models.CASCADE, related_name='complains')


class GiveAwayOffer(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    give_away_type = models.CharField(max_length=20)
    description = models.CharField(max_length=1024)
    photo_telegram_id = models.CharField(max_length=150, null=True, blank=True)
    photo_telegram_url = models.CharField(max_length=500, null=True, blank=True)
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE)


class TelegramUserComplain(models.Model):
    text = models.CharField(max_length=500)
    user_from = models.ForeignKey(TelegramUser, on_delete=models.SET_NULL, blank=True, null=True, related_name='owned_user_complains')
    user_to = models.ForeignKey(TelegramUser, on_delete=models.SET_NULL, blank=True, null=True, related_name='presented_complains')



class HelpRequestReaction(models.Model):
    help_request = models.ForeignKey(HelpRequest, on_delete=models.CASCADE, related_name='reaction')
    owner_reaction = models.CharField(max_length=5, blank=True, null=True)
    helper_reaction = models.CharField(max_length=5, blank=True, null=True)
    helper_id = models.IntegerField()

    class Reactions:
        YES = 'yes'
        NO = 'no'
