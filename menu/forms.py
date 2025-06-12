from django import forms
from .models import MenuBakso, Pemesanan

class MenuBaksoForm(forms.ModelForm):
    class Meta:
        model = MenuBakso
        fields = '__all__'

class PemesananForm(forms.ModelForm):
    class Meta:
        model = Pemesanan
        fields = ['nama_pelanggan', 'nomor_meja', 'keterangan_pesanan'] 