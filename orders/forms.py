from django import forms

class GuestCheckoutForm(forms.Form):
    email = forms.EmailField()
    full_name = forms.CharField(max_length=200)

    address1 = forms.CharField(max_length=200)
    address2 = forms.CharField(max_length=200, required=False)
    city = forms.CharField(max_length=100)
    state = forms.CharField(max_length=100)
    postal_code = forms.CharField(max_length=20)
    country = forms.CharField(max_length=2, initial="US")
