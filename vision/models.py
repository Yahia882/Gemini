from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
User= get_user_model()




class webApp(models.Model):
    user = models.ForeignKey(User, related_name="images", on_delete=models.CASCADE)
    name = models.CharField(max_length=100,blank=False,null=False)
    pages = models.JSONField(blank=True,null=True,default=dict)

class Profile(models.Model):
    user = models.OneToOneField(User, related_name="profile", on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to="avatar", blank=True)
    currentWeb = models.OneToOneField(webApp, on_delete=models.CASCADE,null=True,blank=True)
    def __str__(self):
        return self.user.username
    

