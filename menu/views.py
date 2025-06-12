from django.shortcuts import render, redirect, get_object_or_404
from .forms import MenuBaksoForm

from django.shortcuts import render, redirect, get_object_or_404
from .models import MenuBakso, Pemesanan, ItemPesanan
from django.db.models import Sum

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

        pesanan = Pemesanan.objects.create(
            nama_pelanggan=nama_pelanggan,
            nomor_meja=nomor_meja
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
