import requests
import re

# ====================================================================
# I. KONFIGURASI GLOBAL
# ====================================================================

ALL_POSITIVE_KEYWORDS = {
    "EVENT_ONLY": ["EVENT", "SEA GAMES", "PREMIER LEAGUE", "LA LIGA", "SERIE A", "BUNDESLIGA", "LIGUE 1", "EREDIVISIE", "LIGA 1 INDONESIA", "LIGA PRO SAUDI"],
    "SPORTS_LIVE": ["SPORT", "SPORTS", "LIVE", "LANGSUNG", "OLAHRAGA", "MATCH", "LIGA", "FOOTBALL", "BEIN", "SPOT", "BE IN"],
    "NASIONAL_ID": [
        "INDONESIA", "NASIONAL", "LOKAL", "DAERAH",
        "RCTI", "SCTV", "INDOSIAR", "TRANS", "MNC", "GTV", "GLOBAL TV", 
        "INEWS", "TVONE", "TV ONE", "METRO", "KOMPAS", "NET", "RTV", 
        "TVRI", "BTV", "CNN INDONESIA", "CNBC", "JAK TV", "JTV"
    ],
    "KIDS": [
        "KIDS", "ANAK", "CARTOON", "KARTUN", "NICKELODEON", "NICK JR", 
        "DISNEY", "CARTOON NETWORK", "CN", "BOOMERANG", "BABY", 
        "ANIMATION", "ANIMASI", "TOON", "CERIA", "MENTARI"
    ],
    "KNOWLEDGE": [
        "KNOWLEDGE", "EDUCATION", "EDUKASI", "PENGETAHUAN", "DISCOVERY", 
        "NATIONAL GEOGRAPHIC", "NAT GEO", "NATGEO", "HISTORY", 
        "ANIMAL PLANET", "SCIENCE", "SAINS", "DOCUMENTARY", "DOKUMENTER", "WILD"
    ]
}

GLOBAL_BLACKLIST_URLS = {
    "https://bit.ly/428RaFW",
    "https://iili.io/KfT7PJ2.jpg",
    "https://drive.google.com/uc?export=download&id=12slpj4XW5B5SlR9lruuZ77_NPtTHKKw8&usp",
    "https://shorter.me/SNozg",
    "https://kuk1.modprimus.cfd/kuk3/usergendx0slfk9QssDx9lgxlsdmqrnd.m3u8",
    "https://kuk1.modprimus.cfd/kuk2/usergendx0ul2J8tsDx9lgcddwqrnd.m3u8",
    "https://kudos111.terranovax1.cfd/kuk4/usergendx0thc60skrdnnd.m3u8",
    "https://pulse1.zalmora.cfd/kuk1/usergendx472snx93kdgwqrnd.m3u8",
}

CONFIGURATIONS = [
    {
        "urls": ["https://bit.ly/KPL203", "https://liveevent.iptvbonekoe.workers.dev", "https://deccotech.online/tv/tvstream.html", "https://freeiptv2026.tsender57.workers.dev"],
        "output_file": "event_combined.m3u",
        "keywords": ALL_POSITIVE_KEYWORDS["EVENT_ONLY"],
        "description": "EVENT: Gabungan dari beberapa sumber"
    },
    {
        "urls": ["https://raw.githubusercontent.com/mimipipi22/lalajo/refs/heads/main/playlist25", "https://deccotech.online/tv/tvstream.html", "https://s.id/semartv"],
        "output_file": "sports_combined.m3u",
        "keywords": ALL_POSITIVE_KEYWORDS["SPORTS_LIVE"],
        "description": "SPORTS: Gabungan dari sumber Live"
    },
    {
        "urls": ["https://s.id/semartv", "https://liveevent.iptvbonekoe.workers.dev", "https://freeiptv2026.tsender57.workers.dev", "https://raw.githubusercontent.com/mimipipi22/lalajo/refs/heads/main/playlist25"],
        "output_file": "nasional_combined.m3u",
        "keywords": ALL_POSITIVE_KEYWORDS["NASIONAL_ID"],
        "description": "NASIONAL: Gabungan Saluran TV Indonesia & Lokal"
    },
    {
        "urls": ["https://s.id/semartv", "https://liveevent.iptvbonekoe.workers.dev", "https://freeiptv2026.tsender57.workers.dev", "https://raw.githubusercontent.com/mimipipi22/lalajo/refs/heads/main/playlist25"],
        "output_file": "kids_combined.m3u",
        "keywords": ALL_POSITIVE_KEYWORDS["KIDS"],
        "description": "KIDS: Gabungan Saluran Anak & Kartun"
    },
    {
        "urls": ["https://s.id/semartv", "https://liveevent.iptvbonekoe.workers.dev", "https://freeiptv2026.tsender57.workers.dev", "https://raw.githubusercontent.com/mimipipi22/lalajo/refs/heads/main/playlist25"],
        "output_file": "knowledge_combined.m3u",
        "keywords": ALL_POSITIVE_KEYWORDS["KNOWLEDGE"],
        "description": "KNOWLEDGE: Gabungan Saluran Edukasi & Dokumenter"
    },
]

# Regex untuk mengambil group-title
GROUP_TITLE_REGEX = re.compile(r'group-title="([^"]*)"', re.IGNORECASE)
# Regex untuk membersihkan karakter (hanya alphanumeric dan spasi)
CLEANING_REGEX = re.compile(r'[^a-zA-Z0-9\s]+')

# ====================================================================
# II. FUNGSI UTAMA FILTERING
# ====================================================================

def get_ott_headers():
    """HTTP Headers palsu untuk mem-bypass blokir dasar dari link OTT / Shortlink."""
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
        "Origin": "https://www.google.com",
        "Referer": "https://www.google.com/"
    }

def filter_m3u_by_config(config):
    urls = config["urls"]
    output_file = config["output_file"]
    keywords = config["keywords"]
    description = config["description"]

    print(f"\n--- Memproses [{description}] ---")
    
    filtered_lines = ["#EXTM3U"]
    total_entries = 0
    
    for url in urls:
        if not url:
            continue
            
        print(f"  > Mengunduh dari: {url}")
        
        try:
            response = requests.get(url, headers=get_ott_headers(), timeout=(10, 30), stream=True, allow_redirects=True)
            response.raise_for_status()
            
            current_block = []   # Array untuk menampung 1 blok utuh (#EXTINF, #EXTGRP, URL, dll)
            current_extinf = ""  # String untuk menyimpan teks #EXTINF demi pencocokan regex
            
            for raw_line in response.iter_lines():
                if not raw_line:
                    continue
                    
                line = raw_line.decode('utf-8', errors='ignore').strip()
                
                # 1. Jika baris adalah info channel, MULAI BLOK BARU
                if line.startswith("#EXTINF"):
                    current_block = [line] # Membuka penampung blok baru
                    current_extinf = line
                    
                # 2. Jika baris berupa tag tambahan (seperti #EXTGRP, #KODIPROP), MASUKKAN KE BLOK
                elif line.startswith("#"):
                    if current_block: # Jika blok sedang terbuka
                        current_block.append(line)
                    
                # 3. Jika bukan komentar dan panjang > 5, ini pasti URL. TUTUP BLOK & PROSES.
                elif len(line) > 5:
                    stream_url = line
                    
                    # Pastikan kita punya blok channel yang valid
                    if current_block and current_extinf:
                        if stream_url not in GLOBAL_BLACKLIST_URLS:
                            
                            # Ekstrak metadata hanya dari baris #EXTINF
                            group_match = GROUP_TITLE_REGEX.search(current_extinf)
                            raw_group_title = group_match.group(1) if group_match else ""
                            
                            if "," in current_extinf:
                                raw_channel_name = current_extinf.split(',', 1)[1]
                            else:
                                raw_channel_name = current_extinf
                            
                            # Bersihkan teks untuk pencocokan
                            clean_group_title = CLEANING_REGEX.sub(' ', raw_group_title).upper()
                            clean_channel_name = CLEANING_REGEX.sub(' ', raw_channel_name).upper()
                            
                            # Cocokkan dengan kata kunci
                            is_match = any(k in clean_group_title or k in clean_channel_name for k in keywords)
                            
                            # Jika cocok, masukkan SEMUA isi blok tersebut ditambah URL-nya
                            if is_match:
                                current_block.append(stream_url) # Tambahkan URL di akhir blok
                                filtered_lines.extend(current_block) # Gabungkan seluruh blok ke output final
                                total_entries += 1
                                
                        # Kosongkan penampung blok agar siap untuk channel berikutnya
                        current_block = []
                        current_extinf = ""
                        
        except requests.exceptions.RequestException as e:
            print(f"  > WARNING: Gagal memproses {url}. Error: {e}")
            continue
            
    print(f"Total {total_entries} saluran difilter dari kategori ini.")
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write('\n'.join(filtered_lines) + '\n')
    print(f"Playlist [{output_file}] berhasil disimpan.")

# ====================================================================
# III. EKSEKUSI
# ====================================================================

if __name__ == "__main__":
    print("Memulai Multi-Filter M3U (Optimized & OTT Supported)...")
    for config in CONFIGURATIONS:
        filter_m3u_by_config(config)
    print("\nProses Multi-Filter selesai. Semua 5 file M3U siap digunakan!")
