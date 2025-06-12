from django.db import models

class MenuBakso(models.Model):
    nama = models.CharField(max_length=100)
    deskripsi = models.TextField()
    harga = models.DecimalField(max_digits=10, decimal_places=2)
    tersedia = models.BooleanField(default=True)

    def __str__(self):
        return self.nama

class Pemesanan(models.Model):
    STATUS_PESANAN = (
        ('proses', 'Diproses'),
        ('selesai', 'Selesai'),
    )

    nama_pelanggan = models.CharField(max_length=100, blank=True)
    nomor_meja = models.CharField(max_length=10)
    tanggal_pesan = models.DateTimeField(auto_now_add=True)
    sudah_dibayar = models.BooleanField(default=False)
    keterangan_pesanan = models.TextField(blank=True, null=True)

    # Tambahan untuk monitoring DAPUR
    status = models.CharField(max_length=20, choices=STATUS_PESANAN, default='proses')
    jumlah_item = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Meja {self.nomor_meja} - {self.nama_pelanggan or 'Anonim'}"

class ItemPesanan(models.Model):
    pemesanan = models.ForeignKey(Pemesanan, on_delete=models.CASCADE, related_name='item_pesanan')
    menu = models.ForeignKey(MenuBakso, on_delete=models.CASCADE)
    jumlah = models.PositiveIntegerField()
    
    def subtotal(self):
        return self.menu.harga * self.jumlah