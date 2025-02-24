from arrow import now
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.core.exceptions import ValidationError
from .utils.badword_filter import contains_bad_words


# CustomUserManager สำหรับจัดการผู้ใช้
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

# โมเดล ผู้ใช้
class CustomUser(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    account_name = models.CharField(max_length=100, unique=True)
    gender = models.CharField(max_length=10, choices=[('M', 'ชาย'), ('F', 'หญิง')])
    age = models.IntegerField()
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)  # ฟิลด์เบอร์โทรศัพท์
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)  # ฟิลด์รูปโปรไฟล์
    is_active = models.BooleanField(default=True)

    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'account_name', 'gender', 'age']

    objects = CustomUserManager()

    def __str__(self):
        return self.account_name

# โมเดล Profile
class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    account_name = models.CharField(max_length=100, unique=True)
    age = models.IntegerField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.account_name
    


# โมเดล Cat
class CatProfile(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cat_name = models.CharField(max_length=100,null=True)
    cat_age = models.IntegerField(default= 0,null=True)
    cat_breed = models.CharField(max_length=100,null=True, default='Unknown')
    cat_gender = models.CharField(max_length=20,null=True)
    cat_birthday = models.DateField(default=timezone.now,null=True)
    cat_fav = models.CharField(max_length=100,null=True)
    catprofile_image = models.ImageField(upload_to='catprofile_image/', null=True, blank=True)

    class Meta:
        # คนใช้ต้องมีแมวที่ชื่อแมวไม่ซ้ำกัน
        constraints = [
            models.UniqueConstraint(fields=['owner', 'cat_name'], name='unique_owner_cat')
        ]
    def __str__(self):
        return f"{self.cat_name} ({self.owner.username})"

class Diary(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)  # เชื่อมกับผู้ใช้
    date = models.DateField()
    content = models.TextField()  # ข้อความที่ต้องการวิเคราะห์
    image = models.ImageField(upload_to='diary_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    label = models.IntegerField(choices=[(0, 'Negative'), (1, 'Positive')], null=True, blank=True)  # Sentiment Label

    def __str__(self):
        return f"Diary on {self.date}"
    
class Advice(models.Model):
    CATEGORY_CHOICES = [
        ('อาหารสำหรับแมว', 'อาหารสำหรับแมว'),
        ('โรคที่เสี่ยงจะเป็นในแต่ละวัย', 'โรคที่เสี่ยงจะเป็นในแต่ละวัย'),
        ('การรักษาความสะอาดของแมว', 'การรักษาความสะอาดของแมว'),
    ]
    # ทำให้ user สามารถเป็น None (AnonymousUser) ได้
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    category = models.CharField(max_length=500, choices=CATEGORY_CHOICES)
    advice_text = models.TextField()
    created_at = models.DateTimeField(default=now)

    def clean(self):
        """ ตรวจสอบคำหยาบก่อนบันทึก """
        if contains_bad_words(self.advice_text):
            raise ValidationError("ข้อความมีคำไม่เหมาะสม กรุณาแก้ไขก่อนบันทึก")

    def save(self, *args, **kwargs):
        self.clean()  # เรียกใช้ clean() เพื่อตรวจสอบก่อนบันทึก
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username if self.user else 'Anonymous'} - {self.category}"
    
class DiaryVideo(models.Model):
    title = models.CharField(max_length=255)
    video_file = models.FileField(upload_to='diary_videos/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title