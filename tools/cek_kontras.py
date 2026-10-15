"""Cek rasio kontras WCAG AA pasangan warna yang dipakai di style.css."""


def luminansi(hex_warna: str) -> float:
    hex_warna = hex_warna.lstrip("#")
    kanal = [int(hex_warna[i: i + 2], 16) / 255 for i in (0, 2, 4)]
    kanal = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in kanal]
    return 0.2126 * kanal[0] + 0.7152 * kanal[1] + 0.0722 * kanal[2]


def rasio(a: str, b: str) -> float:
    la, lb = luminansi(a), luminansi(b)
    terang, gelap = max(la, lb), min(la, lb)
    return (terang + 0.05) / (gelap + 0.05)


PASANGAN = [
    ("teks utama di atas kertas", "#241d17", "#f4ede1", 4.5),
    ("teks utama di atas kartu", "#241d17", "#fbf7ef", 4.5),
    ("teks redup di atas kertas", "#574c40", "#f4ede1", 4.5),
    ("teks redup di atas kartu", "#574c40", "#fbf7ef", 4.5),
    ("tautan aksen di atas kertas", "#a6402a", "#f4ede1", 4.5),
    ("teks tombol putih di atas aksen", "#ffffff", "#a6402a", 4.5),
    ("teks tombol putih di atas aksen-tua", "#ffffff", "#8a3421", 4.5),
    ("teks mark di atas latar mark", "#241d17", "#f3e1b3", 4.5),
    ("teks galat di atas latar galat", "#74291a", "#f8eae4", 4.5),
    ("teks kaki halaman di atas kertas", "#574c40", "#f4ede1", 4.5),
    ("angka besar di atas kertas", "#241d17", "#f4ede1", 3.0),
    ("nomor peringkat di atas kertas", "#8e7f68", "#f4ede1", 3.0),
    ("placeholder input di atas kartu", "#6d6153", "#fbf7ef", 4.5),
    ("batas input di atas kartu", "#8e7f68", "#fbf7ef", 3.0),
    ("isian paginasi aktif", "#f4ede1", "#241d17", 4.5),
]

gagal = 0
for nama, depan, belakang, minimum in PASANGAN:
    nilai = rasio(depan, belakang)
    status = "PASS" if nilai >= minimum else "FAIL"
    if nilai < minimum:
        gagal += 1
    print(f"{status}  {nilai:5.2f}:1 (min {minimum})  {nama}")

print(f"\n{len(PASANGAN) - gagal}/{len(PASANGAN)} pasangan lulus")
