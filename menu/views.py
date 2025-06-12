from django.shortcuts import render, redirect, get_object_or_404
from .forms import MenuBaksoForm

from django.shortcuts import render, redirect, get_object_or_404
from .models import MenuBakso, Pemesanan, ItemPesanan
from django.db.models import Sum

from django.db.models.functions import TruncDate
from django.db.models import Count
import json
from django.http import JsonResponse
from django.db.models.functions import TruncDate
from django.db.models import Count, Sum
from datetime import datetime

def dashboard_view(request):
    bulan = request.GET.get('bulan')  # format: 01, 02, dst
    tahun = request.GET.get('tahun')  # format: 2025

    pesanan = Pemesanan.objects.all()

    if bulan and tahun:
        pesanan = pesanan.filter(
            tanggal_pesan__month=int(bulan),
            tanggal_pesan__year=int(tahun)
        )

    # Grafik 1: Jumlah Pemesanan per Tanggal
    data_pesanan = (
        pesanan.annotate(tanggal=TruncDate('tanggal_pesan'))
        .values('tanggal')
        .annotate(jumlah=Count('id'))
        .order_by('tanggal')
    )

    # Grafik 2: Total Penjualan per Hari
    data_penjualan = (
        pesanan.annotate(tanggal=TruncDate('tanggal_pesan'))
        .values('tanggal')
        .annotate(total=Sum('item_pesanan__menu__harga'))
        .order_by('tanggal')
    )

    # Grafik 3: Menu Terlaris
    from .models import ItemPesanan
    data_menu = (
        ItemPesanan.objects.filter(pemesanan__in=pesanan)
        .values('menu__nama')
        .annotate(total=Sum('jumlah'))
        .order_by('-total')
    )

    context = {
        'labels_pesanan': [str(d['tanggal']) for d in data_pesanan],
        'values_pesanan': [d['jumlah'] for d in data_pesanan],

        'labels_penjualan': [str(d['tanggal']) for d in data_penjualan],
        'values_penjualan': [d['total'] for d in data_penjualan],

        'labels_menu': [d['menu__nama'] for d in data_menu],
        'values_menu': [d['total'] for d in data_menu],

        'bulan': bulan,
        'tahun': tahun,

        'bulan_list': ['01','02','03','04','05','06','07','08','09','10','11','12'],
        'tahun_list': ['2023', '2024', '2025'],
    }

    return render(request, 'menu/dashboard.html', context)


def daftar_menu(request):
    menus = MenuBakso.objects.all()
    return render(request, 'menu/daftar_menu.html', {'menus': menus})

def tambah_menu(request):
    form = MenuBaksoForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('daftar_menu')
    return render(request, 'menu/form_menu.html', {'form': form, 'title': 'Tambah Menu'})

def edit_menu(request, pk):
    menu = get_object_or_404(MenuBakso, pk=pk)
    form = MenuBaksoForm(request.POST or None, instance=menu)
    if form.is_valid():
        form.save()
        return redirect('daftar_menu')
    return render(request, 'menu/form_menu.html', {'form': form, 'title': 'Edit Menu'})

def hapus_menu(request, pk):
    menu = get_object_or_404(MenuBakso, pk=pk)
    if request.method == 'POST':
        menu.delete()
        return redirect('daftar_menu')
    return render(request, 'menu/konfirmasi_hapus.html', {'menu': menu})



# Daftar semua pesanan
def daftar_pemesanan(request):
    pemesanan_list = Pemesanan.objects.all().order_by('-tanggal_pesan')
    return render(request, 'menu/daftar_pemesanan.html', {'pemesanan_list': pemesanan_list})

# Form tambah pesanan
def tambah_pemesanan(request):
    menu_list = MenuBakso.objects.all()

    if request.method == 'POST':
        nama_pelanggan = request.POST.get('nama_pelanggan', '')
        nomor_meja = request.POST.get('nomor_meja')
        keterangan = request.POST.get('keterangan_pesanan', '')  # ✅ ambil isi textarea

        pesanan = Pemesanan.objects.create(
            nama_pelanggan=nama_pelanggan,
            nomor_meja=nomor_meja,
            keterangan_pesanan=keterangan  # ✅ simpan ke database
        )

        for menu in menu_list:
            jumlah = int(request.POST.get(f'menu_{menu.id}', 0))
            if jumlah > 0:
                ItemPesanan.objects.create(
                    pemesanan=pesanan,
                    menu=menu,
                    jumlah=jumlah
                )

        return redirect('daftar_pemesanan')

    return render(request, 'menu/form_pemesanan.html', {
        'menu_list': menu_list,
        'title': 'Tambah Pesanan',
        'nama_pelanggan': '',
        'nomor_meja': '',
        'keterangan_pesanan': '',  # ✅ untuk isi awal textarea
    })


# Detail pesanan + tombol bayar
def detail_pemesanan(request, pesanan_id):
    pesanan = get_object_or_404(Pemesanan, id=pesanan_id)
    item_list = pesanan.item_pesanan.all()
    total_harga = sum([item.subtotal() for item in item_list])

    return render(request, 'menu/detail_pemesanan.html', {
        'pesanan': pesanan,
        'total_harga': total_harga,
    })

# Bayar pesanan
def bayar_pemesanan(request, pesanan_id):
    pesanan = get_object_or_404(Pemesanan, id=pesanan_id)
    if request.method == 'POST':
        pesanan.sudah_dibayar = True
        pesanan.save()
    return redirect('daftar_pemesanan')

# Menu kasir: tampilkan semua yang belum dibayar
def kasir_view(request):
    pesanan_list = Pemesanan.objects.filter(sudah_dibayar=False)
    for p in pesanan_list:
        total = p.item_pesanan.aggregate(
            total=Sum('menu__harga')
        )['total']
        p.total = sum([item.subtotal() for item in p.item_pesanan.all()])

    return render(request, 'menu/kasir.html', {
        'pesanan_list': pesanan_list
    })
