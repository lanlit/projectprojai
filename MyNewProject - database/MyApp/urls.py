from django.urls import path
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views


from .views import *

# -------------------------
# URL Patterns
# -------------------------

urlpatterns = [
    # Header and Authentication
    path('', header_view, name='header'),
    path('header/', header_view, name='header'),
    path('home/', home_view, name='home'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register_view'),
    path('logout/', LogoutView.as_view(), name='logout'),
    # ตัวอย่างใน `urls.py`
    #path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    #path('logout/', logout_view, name='logout'),
    # Profile and Cat Profile
    path('profile/', profile_view, name='profile_view'),
     path('profile_edit/', edit_profile, name='profile_edit'), 
    path('save_profile/', save_profile, name='save_profile'),
    #path('cat_profile/',cat_profile_update_view , name='cat_profile'),
    #path('cat/profile/update/', cat_profile_update_view, name='cat_profile_update'),
    path('cat_profile/', cat_profile_view, name='cat_profile'),
    path('cat_profile/edit/<int:id>/', edit_cat_profile, name='cat_edit'),
    # path('cat_profile/edit/<int:cat_id>/',edit_cat_profile, name='cat_edit'),  # เพิ่ม URL สำหรับหน้าแก้ไข
    path('cat_profile/create/',create_cat_profile, name='cat_create'),  # เพิ่ม URL นี้สำหรับหน้าเพิ่มข้อมูลแมว
    #path('cat_edit/', cat_profile_update_view, name='edit_cat_profile'),
    #path('cat_profile/save/', save_cat_info, name='save_cat_info'),
    


    # Diary 
    path('diary/', diary_view, name='diary_view'),
    path('list/', list_view, name='list_view'),
    path('diary_form/', save_diary, name='diary_form'),
    path('diary/<int:diary_id>/', diary_detail_view, name='diary_detail'),
    path('diary/<int:diary_id>/delete/', delete_diary_view, name='delete_diary'),
    

    # Memory Video
    path('select_year/', select_year, name='select_year'),  # หน้าเลือกปี
    path('generate_video/',generate_positive_diary_video, name='generate_video'),  # การสร้างวิดีโอ
    path('positive_video/',show_video, name='positive_video'),  # หน้าแสดงวิดีโอ

    # Advice
    path('advice/list/', advice_list, name='advice_list'),
    path('advice/', advice_form_view, name='advice'),
    path('advice/form/', advice_form_view, name='advice_form'),
    path('save-advice/', save_advice, name='save_advice'),
    

    # Password Reset

    path('password_reset/', auth_views.PasswordResetView.as_view(template_name="reset_password/reset_password.html"), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name="reset_password/reset_password_sent.html"), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="reset_password/reset_password_confirm.html"), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name="reset_password/reset_password_complete.html"), name='password_reset_complete'),

   
]


# -------------------------
# Media Configuration (DEBUG Mode Only)
# -------------------------

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

