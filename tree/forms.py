from django import forms
class BuyForm(forms.Form):
    amount = forms.IntegerField( label = "amount",required=False)
   