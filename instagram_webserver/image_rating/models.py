# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Faces(models.Model):
    username = models.CharField(max_length=255, blank=True, null=True)
    score = models.FloatField(blank=True, null=True)
    date = models.CharField(max_length=255, blank=True, null=True)
    time = models.CharField(max_length=255, blank=True, null=True)
    photo_id = models.IntegerField(blank=True, null=True)
    url = models.CharField(max_length=1000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'faces'


class FacesNew(models.Model):
    username = models.CharField(max_length=255, blank=True, null=True)
    score = models.FloatField(blank=True, null=True)
    taken_at = models.CharField(max_length=255, blank=True, null=True)
    photo_id = models.CharField(max_length=255, blank=True, null=True)
    url = models.CharField(max_length=1000, blank=True, null=True)
    time_entered = models.CharField(max_length=255, blank=True, null=True)
    date_entered = models.CharField(max_length=255, blank=True, null=True)
    filename = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'faces_new'


class Followed(models.Model):
    username = models.CharField(max_length=255, blank=True, null=True)
    followers = models.CharField(max_length=20, blank=True, null=True)
    following = models.CharField(max_length=20, blank=True, null=True)
    date = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=10, blank=True, null=True)
    outcome = models.CharField(max_length=10, blank=True, null=True)
    pictures = models.CharField(max_length=255, blank=True, null=True)
    follow_date = models.CharField(max_length=255, blank=True, null=True)
    ratio_following_to_follower = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(max_length=20, blank=True, null=True)
    outcome_date = models.CharField(max_length=255, blank=True, null=True)
    follow_time = models.CharField(max_length=255, blank=True, null=True)
    profile_from = models.CharField(max_length=255, blank=True, null=True)
    accepted = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'followed'


class FollowedUsers(models.Model):
    username = models.CharField(max_length=255, blank=True, null=True)
    followers = models.CharField(max_length=20, blank=True, null=True)
    following = models.CharField(max_length=20, blank=True, null=True)
    date = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=10, blank=True, null=True)
    pictures = models.CharField(max_length=255, blank=True, null=True)
    follow_date = models.CharField(max_length=255, blank=True, null=True)
    ratio_following_to_follower = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(max_length=20, blank=True, null=True)
    follow_time = models.CharField(max_length=255, blank=True, null=True)
    profile_from = models.CharField(max_length=255, blank=True, null=True)
    score = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'followed_users'


class FollowingUsers(models.Model):
    username = models.CharField(unique=True, max_length=255)
    followers = models.CharField(max_length=20, blank=True, null=True)
    following = models.CharField(max_length=20, blank=True, null=True)
    date = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=10, blank=True, null=True)
    pictures = models.CharField(max_length=255, blank=True, null=True)
    follow_date = models.CharField(max_length=255, blank=True, null=True)
    ratio_following_to_follower = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(max_length=20, blank=True, null=True)
    follow_time = models.CharField(max_length=255, blank=True, null=True)
    profile_from = models.CharField(max_length=255, blank=True, null=True)
    images_collected = models.CharField(max_length=25, blank=True, null=True)
    average_score = models.FloatField(blank=True, null=True)
    min_score = models.FloatField(blank=True, null=True)
    max_score = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'following_users'


class Images(models.Model):
    username = models.CharField(max_length=255, blank=True, null=True)
    date = models.CharField(max_length=255, blank=True, null=True)
    time = models.CharField(max_length=255, blank=True, null=True)
    photo_id = models.IntegerField(blank=True, null=True)
    url = models.CharField(max_length=1000, blank=True, null=True)
    alt = models.CharField(max_length=1000, blank=True, null=True)
    filename = models.CharField(max_length=1000, blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'images'


class ImagesNew(models.Model):
    username = models.CharField(max_length=255)
    taken_at = models.CharField(max_length=255, blank=True, null=True)
    photo_id = models.CharField(max_length=255, blank=True, null=True)
    device_timestamp = models.CharField(max_length=255, blank=True, null=True)
    filename = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=True)
    alt_caption = models.TextField(blank=True, null=True)
    url = models.CharField(max_length=1000, blank=True, null=True)
    time_entered = models.CharField(max_length=255, blank=True, null=True)
    date_entered = models.CharField(max_length=255, blank=True, null=True)
    faces_extracted = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'images_new'


class ProfilePicture(models.Model):
    username = models.CharField(max_length=255, blank=True, null=True)
    score = models.CharField(max_length=255, blank=True, null=True)
    date = models.CharField(max_length=255, blank=True, null=True)
    time = models.CharField(max_length=255, blank=True, null=True)
    photo_id = models.IntegerField(blank=True, null=True)
    url = models.CharField(max_length=1000, blank=True, null=True)
    ml_score = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'profile_picture'


class TrackProfile(models.Model):
    followers = models.CharField(max_length=255, blank=True, null=True)
    following = models.CharField(max_length=255, blank=True, null=True)
    time = models.CharField(max_length=255, blank=True, null=True)
    date = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'track_profile'
