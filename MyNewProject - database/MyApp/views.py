from datetime import timezone
from tracemalloc import BaseFilter
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login , logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *
from .forms import *
from django.core.files.storage import FileSystemStorage
from .utils import *
from django.http import JsonResponse
from moviepy import *
from datetime import date 
import re
from django.utils.timezone import now
from MyApp.utils.badword_filter import *
import pickle
import pandas as pd
from django.contrib.auth.models import AnonymousUser
from datetime import datetime
from .models import Advice  
import cv2,random,textwrap
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
from django.conf import settings
from datetime import datetime,timedelta
from .models import Diary
from nltk import NaiveBayesClassifier as nbc
from pythainlp.tokenize import word_tokenize
import codecs
from itertools import chain
import subprocess
BAD_WORDS = ["เหี้ย", "ควย", "เย็ดแม่", "fuck", "shit", "asshole", "กะหรี่", "หี", "แตด","โป๊","มีเซ็ก"]

def filter_bad_words(text, replacement="***"):
    """ แทนคำหยาบด้วย *** """
    for word in BAD_WORDS:
        pattern = r"\b" + re.escape(word) + r"\b"
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text
# View สำหรับการเข้าสู่ระบบ
def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        
        # ตรวจสอบการยืนยันตัวตนผู้ใช้
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # เปลี่ยนเส้นทางไปยังหน้าแรกหลังจากเข้าสู่ระบบสำเร็จ
        else:
            messages.error(request, 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง')

    return render(request, 'login.html')

# View สำหรับหน้าแรก
def home_view(request):
    return render(request, 'home.html')

def header_view(request):
    return render(request, 'header.html')

def send_new_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            # ค้นหาผู้ใช้งานตามอีเมล
            user = User.objects.get(email=email)
            
            # สร้างรหัสผ่านใหม่
            new_password = generate_random_password()
            user.set_password(new_password)
            user.save()

            # ส่งอีเมลแจ้งรหัสผ่านใหม่
            send_mail(
                'Reset Password',
                f'Your new password is: {new_password}',
                'your_email@example.com',  # ใส่อีเมลผู้ส่ง
                [email],  # ใส่อีเมลผู้รับ
                fail_silently=False,
            )
            return render(request, 'reset_password/reset_password_sent.html')  # ใช้เทมเพลตที่คุณมี
        except User.DoesNotExist:
            return render(request, 'reset_password/reset_password.html', {
                'error': 'ไม่พบผู้ใช้งานที่มีอีเมลนี้ในระบบ'
            })
    return render(request, 'reset_password/reset_password.html')  # หน้าฟอร์มสำหรับกรอกอีเมล


# View สำหรับไดอารี่
def diary_view(request):
    if request.method == 'POST':
        form = DiaryForm(request.POST, request.FILES)  # ตรวจสอบ request.FILES
        if form.is_valid():
            diary_entry = form.save(commit=False)
            diary_entry.owner = request.user  # ระบุเจ้าของ
            diary_entry.save()
            return redirect('list_view')  # หลังบันทึกสำเร็จ
        else:
            print(form.errors)  # Debug: แสดงข้อผิดพลาด
    else:
        form = DiaryForm()
    return render(request, 'diary/diary_form.html', {'form': form})

# View สำหรับโปรไฟล์ผู้ใช้
@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)  # ✅ ดึงข้อมูลโปรไฟล์ล่าสุดของผู้ใช้
    return render(request, 'profile.html', {'profile': profile, 'user': request.user})

@login_required
def cat_profile_view(request):
    # ใช้ filter() เพื่อดึงข้อมูลแมวทั้งหมดที่ผู้ใช้เป็นเจ้าของ
    cat_profiles = CatProfile.objects.filter(owner=request.user)

    if not cat_profiles.exists():  # ตรวจสอบว่ามีข้อมูลแมวหรือไม่
        messages.warning(request, "ยังไม่มีข้อมูลแมว กรุณาเพิ่มข้อมูล")
        return redirect('cat_edit')  # ถ้าไม่มีข้อมูลแมว ให้ไปหน้าแก้ไขข้อมูลแมว

    return render(request, 'cat_profile.html', {'cat_profiles': cat_profiles})  # ส่ง cat_profiles ไปยัง template

def register_view(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        account_name = request.POST['account_name']
        gender = request.POST['gender']
        age = request.POST['age']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
        # ตรวจสอบรหัสผ่าน
        if password == confirm_password:
            # สร้างผู้ใช้ใหม่
            user = CustomUser.objects.create(
                first_name=first_name,
                last_name=last_name,
                account_name=account_name,
                gender=gender,
                age=age,
                email=email,
                password=make_password(password)
            )
            # สร้างโปรไฟล์ให้กับผู้ใช้ใหม่
            Profile.objects.create(user=user)
            return redirect('login')  # เปลี่ยนเส้นทางไปยังหน้าเข้าสู่ระบบ
        else:
            messages.error(request, 'รหัสผ่านไม่ตรงกัน')
            return render(request, 'register.html', {'error': 'รหัสผ่านไม่ตรงกัน'})
    
    return render(request, 'register.html')


# View สำหรับการแก้ไขโปรไฟล์ผู้ใช้และแมว
@login_required
def edit_profile(request):
    # รับข้อมูลผู้ใช้ที่เข้าสู่ระบบ
    user = request.user

    if request.method == 'POST':
        user_form = CustomUserForm(request.POST, instance=user)  # ฟอร์มสำหรับ CustomUser
        profile_form = ProfileForm(request.POST, request.FILES, instance=user.profile)  # ฟอร์มสำหรับ Profile

        # ตรวจสอบว่าแบบฟอร์มทั้งสองถูกต้องหรือไม่
        if user_form.is_valid() and profile_form.is_valid():
            print("ข้อมูลที่ได้รับจากฟอร์ม user_form:", user_form.cleaned_data)  # ดีบักข้อมูลที่รับมาจากฟอร์ม
            print("ข้อมูลที่ได้รับจากฟอร์ม profile_form:", profile_form.cleaned_data)  # ดีบักข้อมูลที่รับมาจากฟอร์ม

            user_form.save()  # บันทึกข้อมูลของ CustomUser
            profile_form.save()  # บันทึกข้อมูลของ Profile

            messages.success(request, 'ข้อมูลโปรไฟล์ได้รับการบันทึกแล้ว!')
            return redirect('profile_view')  # รีไดเรกต์ไปที่หน้าโปรไฟล์หลังจากบันทึกข้อมูลสำเร็จ
        else:
            # แสดงข้อผิดพลาดของฟอร์ม
            print("ข้อผิดพลาดจาก user_form:", user_form.errors)
            print("ข้อผิดพลาดจาก profile_form:", profile_form.errors)

            messages.error(request, 'เกิดข้อผิดพลาดในการบันทึกข้อมูลโปรไฟล์')
    else:
        user_form = CustomUserForm(instance=user)  # โหลดข้อมูลเดิมเมื่อเข้าเพจ
        profile_form = ProfileForm(instance=user.profile)  # โหลดข้อมูลโปรไฟล์เดิม

    return render(request, 'profile_edit.html', {'user_form': user_form, 'profile_form': profile_form})


# View สำหรับรายละเอียดไดอารี่
@login_required
def list_view(request):
    query = request.GET.get('query', '')
    date = request.GET.get('date', '')

    # กรองเฉพาะไดอารี่ของผู้ใช้ที่ล็อกอิน
    diaries = Diary.objects.filter(owner=request.user).order_by('-date')  # เรียงตามวันที่บันทึก

    if query:
        diaries = diaries.filter(content__icontains=query)
    
    if date:  # ถ้ามีค่า date จะทำการกรองตามวันที่
        diaries = diaries.filter(date=date)
        
    return render(request, 'diary/list_diary.html', {'diaries': diaries})
# View สำหรับลบไดอารี่
@login_required
def delete_diary_view(request, diary_id):
    """
    ลบไดอารี่ตาม ID
    """
    diary_entry = get_object_or_404(Diary, id=diary_id, owner=request.user)
    diary_entry.delete()
    return redirect('list_view')  # กลับไปหน้ารายการหลังจากลบ

@login_required
def edit_cat_profile(request):
    # ดึงข้อมูลทั้งหมดของ CatProfile ที่เจ้าของเป็นผู้ใช้ปัจจุบัน
    cat_profiles = CatProfile.objects.filter(owner=request.user)

    if not cat_profiles.exists():
        messages.warning(request, "ยังไม่มีข้อมูลแมว กรุณาเพิ่มข้อมูล")
        return redirect('cat_edit')  # ถ้าไม่มีข้อมูลแมว ให้ไปหน้าแก้ไขข้อมูลแมว

    # สร้าง formset สำหรับหลายๆ แมว
    CatFormSet = modelformset_factory(CatProfile, form=CatForm, queryset=cat_profiles)

    if request.method == 'POST':
        formset = CatFormSet(request.POST, request.FILES)
        if formset.is_valid():
            formset.save()
            messages.success(request, 'บันทึกข้อมูลแมวสำเร็จ!')
            return redirect('cat_profile')  # หรือไปยังหน้าอื่นที่คุณต้องการ
        else:
            messages.error(request, 'เกิดข้อผิดพลาดในการบันทึกข้อมูลแมว')
    else:
        formset = CatFormSet(queryset=cat_profiles)

    return render(request, 'cat_edit.html', {'formset': formset})
    


def logout_view(request):
    logout(request)  # ใช้ logout() เพื่อลบ session ของ user
    return redirect('/')  # หลัง logout ให้ redirect กลับไปที่หน้าแรก

@login_required
def diary_form(request):
    if request.method == 'POST':
        form = DiaryForm(request.POST, request.FILES)  # ใช้ฟอร์ม validate ข้อมูล
        if form.is_valid():
            diary_entry = form.save(commit=False)  # ยังไม่บันทึกลงฐานข้อมูล
            diary_entry.owner = request.user  # กำหนดเจ้าของไดอารี่เป็นผู้ใช้ปัจจุบัน
            diary_entry.save()
            
            # หลังบันทึกสำเร็จให้ไปที่หน้ารายการไดอารี่
            return redirect('list_view')  # ไปที่หน้ารายการไดอารี่หลังบันทึกสำเร็จ
        else:
            print(form.errors)  # Debug ข้อผิดพลาดของฟอร์ม
    else:
        form = DiaryForm()

    # ดึงปีจากไดอารี่ที่มีในฐานข้อมูลของผู้ใช้
    years = Diary.objects.filter(owner=request.user).values('date__year').distinct().order_by('date__year')
    years = [year['date__year'] for year in years]

    return render(request, 'diary/diary_form.html', {'form': form, 'years': years})



# ฟังก์ชัน[ยันทึกไดอารี่]
def save_diary(request):
    if request.method == 'POST':
        try:
            diary_content = request.POST.get('content')  # รับข้อมูลเนื้อหาจากฟอร์ม
            diary_date = request.POST.get('date')  # รับข้อมูลวันที่จากฟอร์ม
            diary_image = request.FILES.get('image')  # รับไฟล์ภาพจากฟอร์ม

            if not diary_content or not diary_date:  # ตรวจสอบว่าไม่มีเนื้อหา หรือวันที่
                messages.error(request, 'กรุณากรอกเนื้อหาของไดอารี่และเลือกวันที่')  # แจ้งเตือนหากไม่มีการกรอกเนื้อหา
                return redirect('diary_form')  # เปลี่ยนเส้นทางกลับไปที่ฟอร์ม

            # บันทึกข้อมูลไดอารี่ลงในฐานข้อมูล
            new_diary = Diary(content=diary_content, date=diary_date, image=diary_image)
            new_diary.save()

            # แสดงข้อความสำเร็จ
            messages.success(request, 'ไดอารี่ถูกบันทึกเรียบร้อยแล้ว!')
            return redirect('list_view')  # เปลี่ยนเส้นทางไปที่หน้าแสดงรายการไดอารี่
        
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการบันทึกไดอารี่: {e}")
            messages.error(request, f'เกิดข้อผิดพลาดในการบันทึกไดอารี่: {e}')
            return redirect('diary_form')

    return render(request, 'diary/diary_form.html')


def diary_detail_view(request, diary_id):
    diary_entry = get_object_or_404(Diary, id=diary_id, owner=request.user)
    return render(request, 'diary/diary_detail.html', {'diary_entry': diary_entry})

def advice_list(request):
    query = request.GET.get('query', '')
    date = request.GET.get('date', '')

    # ดึงข้อมูลคำแนะนำทั้งหมด
    advices = Advice.objects.all()

    # ✅ ตรวจสอบชื่อผู้ใช้ ถ้าไม่มีให้ตั้งค่าเป็น "ไม่ระบุตัวตน"
    for advice in advices:
        if advice.user:
            advice.display_name = f"{advice.user.first_name} {advice.user.last_name}".strip()
        else:
            advice.display_name = "ไม่ระบุตัวตน"

    # กรองข้อมูลตามข้อความค้นหา
    if query:
        advices = advices.filter(
            Q(category__icontains=query) | Q(advice_text__icontains=query)
        )

    # กรองข้อมูลตามวันที่
    if date:
        advices = advices.filter(created_at__date=date)

    return render(request, 'advice_list.html', {'advices': advices})


#@login_required
def advice_saved_view(request):
    # คุณสามารถส่ง context ไปยัง template ถ้ามีข้อมูลเพิ่มเติมที่ต้องการแสดง
    context = {}
    return render(request, 'advice_saved.html', context)



def create_cat_profile(request):
    if request.method == 'POST':
        form = CatForm(request.POST, request.FILES)
        if form.is_valid():
            new_cat = form.save(commit=False)
            new_cat.owner = request.user  # ตั้งค่า owner ให้ตรงกับผู้ใช้ปัจจุบัน
            new_cat.save()
            messages.success(request, 'เพิ่มข้อมูลแมวสำเร็จ!')
            return redirect('cat_profile')  # รีไดเรกต์ไปหน้าโปรไฟล์หลังจากเพิ่มข้อมูล
        else:
            messages.error(request, f'เกิดข้อผิดพลาดในการเพิ่มข้อมูลแมว: {form.errors}')  # เพิ่มการแสดงข้อผิดพลาด
    else:
        form = CatForm()

    return render(request, 'cat_create.html', {'form': form})

@login_required #เอาจริงล่ะอันนี้
def edit_cat_profile(request, id):
    # ดึงข้อมูล CatProfile โดยใช้ id
    cat = get_object_or_404(CatProfile, id=id)
    # ดึงโดยใช้พีเคถ้าใช้ไอดีไม่ได้
    # cat = get_object_or_404(CatProfile, pk=pk, owner=request.user)

    if request.method == 'POST':
        form = CatForm(request.POST, request.FILES, instance=cat)
        if form.is_valid():
            form.save()
            messages.success(request, 'บันทึกข้อมูลแมวสำเร็จ!')
            return redirect('cat_profile')  # เปลี่ยนไปหน้าโปรไฟล์หลังบันทึก
        else:
            messages.error(request, 'เกิดข้อผิดพลาดในการบันทึกข้อมูลแมว')
    else:
        form = CatForm(instance=cat)

    return render(request, 'cat_edit.html', {'form': form, 'cat': cat})

@login_required
def save_profile(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)  # ดึงโปรไฟล์ หรือสร้างถ้าไม่มี

    if request.method == 'POST':
        # ใช้ฟอร์ม ProfileForm ที่รับข้อมูลจาก request.POST และ request.FILES
        form = ProfileForm(request.POST, request.FILES, instance=profile)

        # ตรวจสอบว่า form ถูกต้อง
        if form.is_valid():
            form.save()  # ✅ บันทึกข้อมูลล่าสุดลงในฐานข้อมูล
            messages.success(request, "อัปเดตโปรไฟล์สำเร็จ!")
            return redirect('profile_view')  # ✅ กลับไปที่หน้าโปรไฟล์หลังอัปเดตสำเร็จ
        else:
            # ถ้ามีข้อผิดพลาดในฟอร์ม
            messages.error(request, "เกิดข้อผิดพลาด โปรดลองอีกครั้ง")

    # ถ้าเป็น GET request หรือ POST ที่ไม่ได้ส่งข้อมูลที่ถูกต้อง
    return render(request, 'profile.html', {'profile': profile, 'form': form})


# View สำหรับบันทึกคำแนะนำ
# ฟังก์ชันสำหรับแสดงคำแนะนำตามหมวดหมู่
#@login_required
def save_advice(request):
    if request.method == "POST":
        category = request.POST.get('category', '').strip()
        advice_text = request.POST.get('advice_text', '').strip()
        # ตรวจสอบว่าเป็นผู้ใช้ที่ล็อกอินหรือไม่
        user = request.user if not isinstance(request.user, AnonymousUser) else None
        created_at = request.POST.get('created_at', '')

        # ตรวจสอบข้อมูลที่กรอก
        if not category or not advice_text:
            messages.error(request, "กรุณากรอกข้อมูลให้ครบถ้วน")
            return render(request, 'advice_form.html')  # แสดงฟอร์มใหม่

        # ตรวจสอบหมวดหมู่
        valid_categories = [choice[0] for choice in Advice.CATEGORY_CHOICES]
        if category not in valid_categories:
            messages.error(request, "หมวดหมู่ไม่ถูกต้อง")
            return render(request, 'advice_form.html')  # แสดงฟอร์มใหม่

        # ตรวจสอบและแปลงวันที่
        if created_at:
            try:
                created_at = datetime.strptime(str(created_at), "%Y-%m-%dT%H:%M")
            except ValueError:
                messages.error(request, "รูปแบบวันที่ไม่ถูกต้อง")
                return render(request, 'advice_form.html')  # แสดงฟอร์มใหม่
        else:
            created_at = now()

        # บันทึกข้อมูลลงฐานข้อมูล
        Advice.objects.create(
            user=user,  # กรณีที่ไม่ล็อกอิน user = None
            category=category,
            advice_text=advice_text,
            created_at=created_at
        )

        messages.success(request, "บันทึกคำแนะนำสำเร็จ!")
        return redirect('advice_list')  # ไปที่หน้าแสดงรายการคำแนะนำ

    return render(request, 'advice_form.html')  # ถ้าเป็น GET แสดงฟอร์มใหม่

def advice_form_view(request):
    return render(request, 'advice_form.html')



@login_required
def generate_positive_diary_video(request):
    selected_year = request.GET.get('year')
    selected_music = request.GET.get('music')
    start_time = request.GET.get('start_time', 0)  

    if not selected_year or not selected_music:
        return JsonResponse({'error': 'กรุณาเลือกปีและเพลง'})

    start_date = datetime.strptime(f"{selected_year}-01-01", '%Y-%m-%d').date()
    end_date = datetime.strptime(f"{selected_year}-12-31", '%Y-%m-%d').date()

    diaries = Diary.objects.filter(
        owner=request.user,
        date__range=[start_date, end_date],
        label=1,
        image__isnull=False
    ).order_by('date')

    if not diaries:
        return JsonResponse({'error': 'ไม่พบไดอารี่ที่มีความรู้สึกเชิงบวกในปีนี้ หรือไม่มีรูปภาพในไดอารี่ที่เลือก'})

    random_diaries = random.sample(list(diaries), min(15, len(diaries)))

    temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
    os.makedirs(temp_dir, exist_ok=True)

    # ขนาดรูปภาพที่ต้องการ
    FIXED_WIDTH = 1380
    FIXED_HEIGHT = 1000

    image_files = []
    for diary in random_diaries:
        if diary.image:
            image_path = diary.image.path
            img = cv2.imread(image_path)

            # แปลงเป็น PIL
            pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

            # --- ปรับขนาดโดยคงอัตราส่วน ---
            original_width, original_height = pil_img.size
            ratio = min(FIXED_WIDTH / original_width, FIXED_HEIGHT / original_height)
            new_width = int(original_width * ratio)
            new_height = int(original_height * ratio)
            resized_img = pil_img.resize((new_width, new_height), Image.LANCZOS)

            # --- สร้างพื้นหลังจากภาพเดิมและทำให้เบลอ ---
            background = pil_img.resize((FIXED_WIDTH, FIXED_HEIGHT), Image.LANCZOS)
            background = background.filter(ImageFilter.GaussianBlur(15))  # เบลอพื้นหลัง

            # --- วางรูปที่ถูกปรับขนาดไว้ตรงกลางของพื้นหลังเบลอ ---
            x_offset = (FIXED_WIDTH - new_width) // 2
            y_offset = (FIXED_HEIGHT - new_height) // 2
            background.paste(resized_img, (x_offset, y_offset))

            draw = ImageDraw.Draw(background)

            # ตรวจสอบเส้นทางฟอนต์
            font_path = os.path.abspath(os.path.join(settings.BASE_DIR, "MyApp/static/fonts/Sarabun-Bold.ttf"))
            if not os.path.exists(font_path):
                return JsonResponse({'error': 'ไม่พบไฟล์ฟอนต์ กรุณาตรวจสอบ static/fonts/'})

            font = ImageFont.truetype(font_path, 50)

            # ตัดข้อความให้พอดีกับรูป
            max_width = 40
            wrapped_text = textwrap.fill(diary.content, width=max_width)

            # คำนวณตำแหน่งกึ่งกลางด้านล่าง
            text_bbox = draw.textbbox((0, 0), wrapped_text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            x_position = (FIXED_WIDTH - text_width) // 2
            y_position = FIXED_HEIGHT - text_height - 50  

            # ใส่พื้นหลังดำโปร่งแสงรองรับข้อความ
            # draw.rectangle([(0, y_position - 10), (FIXED_WIDTH, y_position + text_height + 20)], fill=(0, 0, 0, 100))
            draw.text((x_position, y_position), wrapped_text, font=font, fill=(255, 255, 255))

            # แปลงกลับเป็น OpenCV และบันทึก
            img_with_text = cv2.cvtColor(np.array(background), cv2.COLOR_RGB2BGR)
            output_image_path = os.path.join(temp_dir, f"image_{diary.id}.jpg")
            cv2.imwrite(output_image_path, img_with_text)
            image_files.append(output_image_path)

        if not image_files:
            return JsonResponse({'error': 'ไม่พบรูปภาพที่ใช้ได้'})

        # สร้างวิดีโอจากรูปภาพที่มีข้อความ
        video_clips = [ImageClip(img, duration=2).resized((FIXED_WIDTH, FIXED_HEIGHT)) for img in image_files]
        final_video = concatenate_videoclips(video_clips, method="compose")
        
        # ตรวจสอบและใช้เพลงที่เลือก
        music_dir = os.path.join(settings.BASE_DIR, 'static', 'music')
        music_path = os.path.join(music_dir, os.path.basename(selected_music))

        print("Music Path:", music_path)  # Debugging เพื่อตรวจสอบ path

# ตรวจสอบว่าไฟล์มีอยู่จริงหรือไม่
    if not os.path.exists(music_path):
        return JsonResponse({'error': f'ไม่พบไฟล์เพลง: {music_path}'})
    try:
        audio = AudioFileClip(music_path)
        audio_duration = audio.duration  

        start_time = max(float(start_time), 0)  
        end_time = min(start_time + 30, audio_duration)

        if start_time >= audio_duration:
            return JsonResponse({'error': 'เวลาเริ่มต้นเกินความยาวของเพลง'})

        audio = audio.subclipped(start_time, end_time)
        final_video = final_video.with_audio(audio)

    except Exception as e:
        return JsonResponse({'error': f'เกิดข้อผิดพลาดขณะโหลดเพลง: {str(e)}'})

    video_filename = f"positive_memories_{selected_year}.mp4"
    video_path = os.path.join(settings.MEDIA_ROOT, 'videos', video_filename)
    final_video.write_videofile(video_path, codec='libx264', fps=24)

    video_url = os.path.join('/media/videos/', video_filename)

    return render(request, 'diary/positive_video.html', {
        'video_path': video_url,
        'selected_year': selected_year,
        'success': f'วิดีโอความทรงจำที่ดีสำหรับปี {selected_year} ถูกสร้างเรียบร้อยแล้ว'
    })

@login_required
def select_year(request):
    return render(request, 'diary/select_year.html')  # หน้าเลือกปี

def show_video(request):
    video_path = request.GET.get('video_path')
    return render(request, 'diary/positive_video.html', {'video_path': video_path})