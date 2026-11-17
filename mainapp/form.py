from django import forms

class p_add_form(forms.Form):
    Product_ID = forms.IntegerField()
    Product_Name = forms.CharField(max_length=100)
    Product_Price = forms.IntegerField(required=False)
    Product_quantity = forms.IntegerField(show_hidden_initial=1)

class p_edit_form(forms.Form):
    Product_Name= forms.CharField(max_length=100 ,required=False)
    Product_Price = forms.IntegerField(required=False)
    Product_Quantity = forms.IntegerField(required=False)

class register_user(forms.Form):
    Name = forms.CharField(max_length=30)
    Mobile = forms.CharField(max_length=10)
    Password = forms.CharField(widget=forms.PasswordInput())
    Conform_Password = forms.CharField(widget=forms.PasswordInput())

class login_user(forms.Form):
    Mobile = forms.CharField(max_length=10)
    Password = forms.CharField(widget=forms.PasswordInput())

class reset_pass(forms.Form):
    Mobile = forms.CharField(max_length=10)
    New_Password = forms.CharField(widget=forms.PasswordInput())

class make_inventory(forms.Form):
    Enter_Inventory_Name = forms.CharField(
        max_length=100,
        required=True,
        label="Enter Your Store Name",
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g. Rahul Electronics',
            'class': 'w-full rounded-xl border border-slate-300 px-4 py-3'
        })
    )

class make_report(forms.Form):
    date = forms.DateField(
        input_formats=['%d-%m-%Y'],
        widget=forms.DateInput(attrs={
            'type': 'text',
            'placeholder': 'DD-MM-YYYY',
            'id':'manualDate',
            'autocomplete': 'off'
        })
    )