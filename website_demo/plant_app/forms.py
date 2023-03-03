from django import forms
from phonenumber_field.formfields import PhoneNumberField
from .models import CustomerModel, TransactionModel
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

class CustomerModelForm(forms.ModelForm):

    class Meta:
        model = CustomerModel
        fields = ['customer', 'email', 'tel']
        widgets = {
            'customer': forms.TextInput(attrs={'class': 'form-control', 'style': 'width:100%;', "placeholder": "您的大名"}),
            'email': forms.TextInput(attrs={'class': 'form-control', 'style': 'width:100%;', "placeholder": "電子信箱"}),
            'tel': forms.TextInput(attrs={'class': 'form-control', 'style': 'width:100%;', "placeholder": "連絡電話"}),
        }
        labels = {
            'customer': '收件姓名',
            'email': '電子郵件',
            'tel': '聯絡電話',
        }

        # def clean_email(self, *args, **kwargs):
        #     email = self.cleaned_data.get('email')  # 取得樣板所填寫的資料
        #     if email.endswith('@hotmail.com'):
        #         raise forms.ValidationError('不得使用Hotmail電子郵件')
        #     return email

class TranscationModelForm(forms.ModelForm):
    class Meta:
        model = TransactionModel
        fields = ["payment", "delivery", "address", "comment"]
        widgets = {
            'payment': forms.Select(attrs={'class': 'form-control', 'style': 'width:50%'}),
            'delivery': forms.Select(attrs={'class': 'form-control select', 'style': 'width:50%'}),
            'address': forms.TextInput(
                attrs={'class': 'form-control', 'style': 'width:100%;', "placeholder": "請選擇711店家, 宅配地點或是面交地點"}),
            'comment': forms.TextInput(
                attrs={'class': 'form-control', 'style': 'height:100px; width:100%;', "placeholder": "想說的話"}),
        }
        labels = {
            'payment': '付款方式',
            'delivery': '運送方式',
            'address': '交易地址',
            'comment': "備註"
        }
    def __init__(self):
        super().__init__()
        transaction_obj = TransactionModel.objects.all()
        self.fields["payment"].choices = [doc.payment for doc in transaction_obj]
        self.fields["delivery"].choices = [doc.delivery for doc in transaction_obj]

class RegisterModelForm(UserCreationForm):

    username = forms.EmailField(
        label="電子信箱",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'autocomplete': 'email'}),
        error_messages={
            'invalid': '請輸入有效電子信箱',
            'required': '尚未輸入電子信箱',
        }
    )
    password1 = forms.CharField(
        label="密碼",
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        error_messages={'required': '尚未輸入密碼'}
    )
    password2 = forms.CharField(
        label="密碼確認",
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        error_messages={'required': '尚未輸入密碼'}
    )
    error_messages = {
        'password_mismatch': _('兩次密碼輸入不同'),
    }

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')

class LoginModelForm(forms.Form):

    username = forms.EmailField(
        label="電子信箱",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'autocomplete': 'email'}),
        error_messages={
            'invalid': '請輸入有效電子信箱',
            'required': '尚未輸入電子信箱',
        }
    )
    password = forms.CharField(
        label="密碼",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('username', 'password')