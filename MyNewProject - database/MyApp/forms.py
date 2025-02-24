# ลบการ import ผิดๆ ออก
# from cProfile import Profile  # ไม่จำเป็นต้องใช้
from .models import Advice 
from django import forms
from .models import * # import โมเดล Profile ที่ถูกต้อง

class RegisterForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput(), label="ยืนยันรหัสผ่าน")

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'account_name', 'gender', 'age', 'email', 'password']
        widgets = {
            'password': forms.PasswordInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("รหัสผ่านไม่ตรงกัน")

    def save(self, commit=True):
        user = super(RegisterForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])  # เข้ารหัสรหัสผ่านก่อนบันทึก
        if commit:
            user.save()
        return user
    
class CustomUserForm(forms.ModelForm):
    phone_number = forms.CharField(required=True)
    profile_image = forms.ImageField(required=False)

    def clean_account_name(self):
        # ตรวจสอบว่า account_name ซ้ำหรือไม่
        account_name = self.cleaned_data.get('account_name')
        if CustomUser.objects.filter(account_name=account_name).exists():
            raise ValidationError("Account name นี้มีอยู่แล้ว โปรดลองใหม่อีกครั้ง.")
        return account_name

    class Meta:
        model = CustomUser
        fields = ['account_name', 'phone_number', 'profile_image']  # removed 'first_name', 'last_name', 'email', and 'age'

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['account_name', 'phone_number', 'profile_image']  # removed 'email' and 'age'

        
class AdviceForm(forms.ModelForm):
    class Meta:
        model = Advice
        fields = ['category', 'advice_text'] 

class CatForm(forms.ModelForm):
    class Meta:
        model = CatProfile
        fields = ['cat_name', 'cat_age', 'cat_breed', 'cat_gender', 'cat_birthday', 'cat_fav', 'catprofile_image']
        
class DiaryForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})  # ให้เลือกวันที่จากปฏิทิน
    )

    class Meta:
        model = Diary
        fields = ['date', 'content', 'image'] 
        
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'account_name', 'gender', 'age', 'email', 'phone_number', 'profile_image']

class AdviceForm(forms.Form):
    category_choices = [
        ('อาหารสำหรับแมว', 'อาหารสำหรับแมว'),
        ('โรคที่จะเสี่ยงเป็นในแต่ละวัย', 'โรคที่จะเสี่ยงเป็นในแต่ละวัย'),
        ('การรักษาความสะอาดของแมว', 'การรักษาความสะอาดของแมว'),
    ]
    category = forms.ChoiceField(choices=category_choices, label="หมวดหมู่", required=True)
    advice_text = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'เขียนคำแนะนำที่นี่...'}),
        label="คำแนะนำ",
        required=True
    )
    
class CatUpdateForm(forms.ModelForm):
    class Meta:
        model = CatProfile
        fields = '__all__'

class PasswordResetForm(forms.Form):
    email = forms.EmailField(label="อีเมล", max_length=254, required=True)

class VideoForm(forms.ModelForm):
    class Meta:
        model = DiaryVideo
        fields = ['title', 'video_file']