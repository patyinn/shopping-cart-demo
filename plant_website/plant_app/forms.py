from django import forms
from .models import CustomerModel, TransactionModel

class CustomerModelForm(forms.ModelForm):

    class Meta:
        model = CustomerModel
        fields = "__all__"
        widgets = {
            'customer': forms.TextInput(attrs={'class': 'form-control', 'style': 'width:50%;', "placeholder": "您的大名"}),
            'email': forms.TextInput(attrs={'class': 'form-control', 'style': 'width:50%;', "placeholder": "電子信箱"}),
            'tel': forms.TextInput(attrs={'class': 'form-control', 'style': 'width:50%;', "placeholder": "連絡電話"}),
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
        payment = forms.ChoiceField(choices=[doc.payment for doc in TransactionModel.objects.all()])
        delivery = forms.ChoiceField(choices=[doc.delivery for doc in TransactionModel.objects.all()])
        fields = ["payment", "delivery", "address", "comment"]
        widgets = {
            'payment': forms.Select(attrs={'class': 'select'}),
            'delivery': forms.Select(attrs={'class': 'select', 'onchange': 'actionform.submit();'}),
            'address': forms.TextInput(
                attrs={'class': 'form-control', 'style': 'width:50%;', "placeholder": "請選擇711店家, 宅配地點或是面交地點(限捷運景平、景安)"}),
            'comment': forms.TextInput(
                attrs={'class': 'form-control', 'style': 'width:50%;', "placeholder": "想說的話"}),
        }
        labels = {
            'payment': '付款方式',
            'delivery': '運送方式',
            'address': '交易地址',
            'comment': "備註"
        }
