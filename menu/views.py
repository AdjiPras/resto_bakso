from django.shortcuts import render, redirect, get_object_or_404
from .forms import MenuBaksoForm

from django.shortcuts import render, redirect, get_object_or_404
from .models import MenuBakso, Pemesanan, ItemPesanan
from django.db.models import Sum

from django.db.models.functions import TruncDate,  TruncMonth
import json
from django.http import JsonResponse
from django.db.models import Count, Sum
from datetime import datetime
from django.views.decorators.http import require_POST

from django.db.models import F, ExpressionWrapper, DecimalField
from django.core.paginator import Paginator


def dapur_view(request):
    daftar_pesanan = Pemesanan.objects.all().order_by('-id')  # contoh: ambil semua pesanan
    context = {'daftar_pesanan': daftar_pesanan}
    return render(request, 'menu/dapur.html', context)


def dashboard_view(request):
    bulan = request.GET.get('bulan')
    tahun = request.GET.get('tahun')

    pesanan = Pemesanan.objects.all()

    # Filter waktu jika dipilih
    if bulan and tahun:
        pesanan = pesanan.filter(
            tanggal_pesan__month=int(bulan),
            tanggal_pesan__year=int(tahun)
        )

    # Ringkasan
    total_pesanan = pesanan.count()
    pesanan_proses = pesanan.filter(status='proses').count()
    pesanan_selesai = pesanan.filter(status='selesai').count()

    # Grafik 1: Jumlah Pemesanan per Tanggal
    data_pesanan = (
        pesanan.annotate(tanggal=TruncDate('tanggal_pesan'))
        .values('tanggal')
        .annotate(jumlah=Count('id'))
        .order_by('tanggal')
    )

    # Grafik 2: Total Penjualan per Hari (BENAR)
    data_penjualan = (
        pesanan.annotate(tanggal=TruncDate('tanggal_pesan'))
        .values('tanggal')
        .annotate(
            total=Sum(
                ExpressionWrapper(
                    F('item_pesanan__menu__harga') * F('item_pesanan__jumlah'),
                    output_field=DecimalField()
                )
            )
        )
        .order_by('tanggal')
    )

    # Grafik 3: Menu Terlaris
    data_menu = (
        ItemPesanan.objects.filter(pemesanan__in=pesanan)
        .values('menu__nama')
        .annotate(total=Sum('jumlah'))
        .order_by('-total')
    )

    # Monitoring Dapur
    monitoring_dapur = (
        pesanan
        .values('nomor_meja', 'status')
        .annotate(total_pesanan=Count('id'), total_item=Sum('item_pesanan__jumlah'))
        .order_by('nomor_meja')
    )

    # ➕ Daftar Pesanan Terbaru
    daftar_pesanan_terbaru = pesanan.order_by('-tanggal_pesan')[:10]

    # ➕ Daftar Pesanan Terbaru dengan Paginasi
    daftar_pesanan_all = pesanan.order_by('-tanggal_pesan')
    paginator = Paginator(daftar_pesanan_all, 5)  # Ganti 5 sesuai jumlah per halaman
    page_number = request.GET.get('page')
    daftar_pesanan_terbaru = paginator.get_page(page_number)

    context = {
        # Ringkasan
        'total_pesanan': total_pesanan,
        'pesanan_proses': pesanan_proses,
        'pesanan_selesai': pesanan_selesai,

        # Grafik
        'labels_pesanan': [str(d['tanggal']) for d in data_pesanan],
        'values_pesanan': [d['jumlah'] for d in data_pesanan],
        'labels_penjualan': [str(d['tanggal']) for d in data_penjualan],
        'values_penjualan': [float(d['total']) if d['total'] is not None else 0 for d in data_penjualan],
        'labels_menu': [d['menu__nama'] for d in data_menu],
        'values_menu': [d['total'] for d in data_menu],

        # Monitoring Dapur
        'monitoring_dapur': monitoring_dapur,

        # Pesanan Terbaru
        'daftar_pesanan_terbaru': daftar_pesanan_terbaru,

        # Filter bulan/tahun
        'bulan': bulan,
        'tahun': tahun,
        'bulan_list': ['01','02','03','04','05','06','07','08','09','10','11','12'],
        'tahun_list': ['2023', '2024', '2025'],
    }

    return render(request, 'menu/dashboard.html', context)




def dapur_view(request):
    daftar_pesanan = Pemesanan.objects.all().order_by('-tanggal_pesan')
    return render(request, 'menu/dapur.html', {'daftar_pesanan': daftar_pesanan})


def daftar_menu(request):
    menus = MenuBakso.objects.all()
    return render(request, 'menu/daftar_menu.html', {'menus': menus})


# MENU
def tambah_menu(request):
    form = MenuBaksoForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('daftar_menu')
    return render(request, 'menu/form_menu.html', {'form': form, 'title': 'Tambah Menu'})

def edit_menu(request, id):
    menu = get_object_or_404(MenuBakso, id=id)
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
    # pemesanan_list = Pemesanan.objects.all().order_by('-tanggal_pesan')
    pemesanan_list = Pemesanan.objects.prefetch_related('item_pesanan__menu').order_by('-tanggal_pesan')
    context = {
        'pemesanan_list': pemesanan_list
    }
    return render(request, 'menu/daftar_pemesanan.html', context)

# Form tambah pesanan
def tambah_pemesanan(request):
    menu_list = MenuBakso.objects.all()

    if request.method == 'POST':
        print("DEBUG: Tipe request.POST =", type(request.POST))  # Debug jika error

        nama_pelanggan = request.POST.get('nama_pelanggan', '')
        nomor_meja = request.POST.get('nomor_meja')
        keterangan = request.POST.get('keterangan_pesanan', '')

        # Simpan data pemesanan ke database
        pesanan = Pemesanan.objects.create(
            nama_pelanggan=nama_pelanggan,
            nomor_meja=nomor_meja,
            keterangan_pesanan=keterangan
        )

        # Simpan item pesanan (jumlah menu)
        for menu in menu_list:
            try:
                jumlah = int(request.POST.get(f'menu_{menu.id}', 0))
            except (ValueError, TypeError):
                jumlah = 0

            if jumlah > 0:
                ItemPesanan.objects.create(
                    pemesanan=pesanan,
                    menu=menu,
                    jumlah=jumlah
                )

        return redirect('daftar_pemesanan')

    # Mode GET (tampilkan form kosong)
    return render(request, 'menu/form_pemesanan.html', {
        'menu_list': menu_list,
        'title': 'Tambah Pesanan',
        'nama_pelanggan': '',
        'nomor_meja': '',
        'keterangan_pesanan': '',
    })



# DETAIL PESANAN
def detail_pemesanan(request, pesanan_id):
    pesanan = get_object_or_404(Pemesanan, id=pesanan_id)
    item_list = pesanan.item_pesanan.all()
    total_harga = sum([item.subtotal() for item in item_list])

    return render(request, 'menu/detail_pemesanan.html', {
        'pesanan': pesanan,
        'total_harga': total_harga,
    })

# EDIT PESANAN
def edit_pemesanan(request, pesanan_id):
    pesanan = get_object_or_404(Pemesanan, id=pesanan_id)
    menu_list = MenuBakso.objects.all()

    if request.method == 'POST':
        pesanan.nama_pelanggan = request.POST.get('nama_pelanggan', '')
        pesanan.nomor_meja = request.POST.get('nomor_meja')
        pesanan.keterangan_pesanan = request.POST.get('keterangan_pesanan', '')
        pesanan.save()

        pesanan.item_pesanan.all().delete()

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
        'title': 'Edit Pesanan',
        'nama_pelanggan': pesanan.nama_pelanggan,
        'nomor_meja': pesanan.nomor_meja,
        'keterangan_pesanan': pesanan.keterangan_pesanan,
        'pesanan': pesanan,
        'item_pesanan': {item.menu.id: item.jumlah for item in pesanan.item_pesanan.all()}
    })

# HAPUS PESANAN
def hapus_pemesanan(request, pesanan_id):
    pesanan = get_object_or_404(Pemesanan, id=pesanan_id)

    if request.method == 'POST':
        pesanan.delete()
        return redirect('daftar_pemesanan')

    return render(request, 'menu/konfirmasi_hapus.html', {
        'pesanan': pesanan
    })



@require_POST
def ubah_status_pesanan(request, pesanan_id):
    pesanan = get_object_or_404(Pemesanan, id=pesanan_id)
    status_baru = request.POST.get('status')

    if status_baru in ['proses', 'selesai']:
        pesanan.status = status_baru
        pesanan.save()

    return redirect('dashboard')

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
