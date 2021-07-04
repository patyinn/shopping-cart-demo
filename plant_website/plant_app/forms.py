from django import forms
from .models import CustomerModel

class CustomerModelForm(forms.ModelForm):

    class Meta:
        model = CustomerModel
        fields = ['customer', 'email', 'tel', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'style': 'width:50%;', "placeholder": "您的大名"}),
            'email': forms.TextInput(attrs={'class': 'form-control', 'style': 'width:50%;', "placeholder": "電子信箱"}),
            'tel': forms.TextInput(attrs={'class': 'form-control', 'style': 'width:50%;', "placeholder": "連絡電話"}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'style': 'width:50%;', "placeholder": "收貨地址"}),
        }
        labels = {
            'customer': '收件姓名',
            'email': '電子郵件',
            'tel': '聯絡電話',
            'address': '收貨地址',
        }

        # def clean_email(self, *args, **kwargs):
        #     email = self.cleaned_data.get('email')  # 取得樣板所填寫的資料
        #     if email.endswith('@hotmail.com'):
        #         raise forms.ValidationError('不得使用Hotmail電子郵件')
        #     return email