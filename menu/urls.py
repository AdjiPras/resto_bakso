from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),

    # CRUD menu bakso
    path('daftar_menu/', views.daftar_menu, name='daftar_menu'),
    path('tambah/', views.tambah_menu, name='tambah_menu'),
    path('edit/<int:id>/', views.edit_menu, name='edit_menu'),
    path('hapus/<int:id>/', views.hapus_menu, name='hapus_menu'),

    # Pemesanan
    path('pemesanan/', views.daftar_pemesanan, name='daftar_pemesanan'),
    path('pemesanan/tambah/', views.tambah_pemesanan, name='tambah_pemesanan'),
    path('pemesanan/<int:pesanan_id>/', views.detail_pemesanan, name='detail_pemesanan'),
    path('pemesanan/<int:pesanan_id>/bayar/', views.bayar_pemesanan, name='bayar_pemesanan'),
    path('ubah-status/<int:pesanan_id>/', views.ubah_status_pesanan, name='ubah_status_pesanan'),

    path('pemesanan/<int:pesanan_id>/edit/', views.edit_pemesanan, name='edit_pemesanan'),
    path('pemesanan/<int:pesanan_id>/hapus/', views.hapus_pemesanan, name='hapus_pemesanan'),

    # Dapur
    path('dapur/', views.dapur_view, name='dapur_view'),

    # Kasir
    path('kasir/', views.kasir_view, name='kasir_view'),
]