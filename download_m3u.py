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

# --- PERUBAHAN: Menambahkan "category_name" untuk menimpa nama grup di M3U ---
CONFIGURATIONS = [
    {
        "urls": ["https://bit.ly/KPL203", "https://liveevent.iptvbonekoe.workers.dev", "https://deccotech.online/tv/tvstream.html", "https://freeiptv2026.tsender57.workers.dev"],
        "output_file": "event_combined.m3u",
        "keywords": ALL_POSITIVE_KEYWORDS["EVENT_ONLY"],
        "category_name": "EVENT", 
        "description": "EVENT: Gabungan dari beberapa sumber"
    },
    {
        "urls": ["https://raw.githubusercontent.com/mimipipi22/lalajo/refs/heads/main/playlist25", "https://deccotech.online/tv/tvstream.html", "https://s.id/semartv"],
        "output_file": "sports_combined.m3u",
        "keywords": ALL_POSITIVE_KEYWORDS["SPORTS_LIVE"],
        "category_name": "SPORTS",
        "description": "SPORTS: Gabungan dari sumber Live"
    },
    {
        "urls": ["https://s.id/semartv", "https://liveevent.iptvbonekoe.workers.dev", "https://freeiptv2026.tsender57.workers.dev", "https://raw.githubusercontent.com/mimipipi22/lalajo/refs/heads/main/playlist25"],
        "output_file": "nasional_combined.m3u",
        "keywords": ALL_POSITIVE_KEYWORDS["NASIONAL_ID"],
        "category_name": "NASIONAL",
        "description": "NASIONAL: Gabungan Saluran TV Indonesia & Lokal"
    },
    {
        "urls": ["https://s.id/semartv", "https://liveevent.iptvbonekoe.workers.dev", "https://freeiptv2026.tsender57.workers.dev", "https://raw.githubusercontent.com/mimipipi22/lalajo/refs/heads/main/playlist25"],
        "output_file": "kids_combined.m3u",
        "keywords": ALL_POSITIVE_KEYWORDS["KIDS"],
        "category_name": "KIDS",
        "description": "KIDS: Gabungan Saluran Anak & Kartun"
    },
    {
        "urls": ["https://s.id/semartv", "https://liveevent.iptvbonekoe.workers.dev", "https://freeiptv2026.tsender57.workers.dev", "https://raw.githubusercontent.com/mimipipi22/lalajo/refs/heads/main/playlist25"],
        "output_file": "knowledge_combined.m3u",
        "keywords": ALL_POSITIVE_KEYWORDS["KNOWLEDGE"],
        "category_name": "KNOWLEDGE",
        "description": "KNOWLEDGE: Gabungan Saluran Edukasi & Dokumenter"
    },
]

# Regex
GROUP_TITLE_REGEX = re.compile(r'group-title="([^"]*)"', re.IGNORECASE)
CLEANING_REGEX = re.compile(r'[^a-zA-Z0-9\s]+')

# ====================================================================
# II. FUNGSI UTAMA FILTERING
# ====================================================================

def get_ott_headers():
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
    target_category = config["category_name"] # Menarik nama kategori yang dipaksa
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
            
            current_block = []   
            current_extinf = ""  
            
            for raw_line in response.iter_lines():
                if not raw_line:
                    continue
                    
                line = raw_line.decode('utf-8', errors='ignore').strip()
                
                if line.startswith("#EXTINF"):
                    current_block = [line] 
                    current_extinf = line
                    
                elif line.startswith("#"):
                    if current_block: 
                        current_block.append(line)
                    
                elif len(line) > 5:
                    stream_url = line
                    
                    if current_block and current_extinf:
                        if stream_url not in GLOBAL_BLACKLIST_URLS:
                            
                            # Cek pencocokan dengan kata kunci
                            group_match = GROUP_TITLE_REGEX.search(current_extinf)
                            raw_group_title = group_match.group(1) if group_match else ""
                            
                            if "," in current_extinf:
                                raw_channel_name = current_extinf.split(',', 1)[1]
                            else:
                                raw_channel_name = current_extinf
                            
                            clean_group_title = CLEANING_REGEX.sub(' ', raw_group_title).upper()
                            clean_channel_name = CLEANING_REGEX.sub(' ', raw_channel_name).upper()
                            
                            is_match = any(k in clean_group_title or k in clean_channel_name for k in keywords)
                            
                            # --- LOGIKA BARU: MEMAKSA NAMA KATEGORI (OVERWRITE) ---
                            if is_match:
                                extinf_line = current_block[0]
                                
                                # 1. Timpa group-title di dalam #EXTINF
                                if 'group-title="' in extinf_line:
                                    extinf_line = re.sub(r'group-title="[^"]*"', f'group-title="{target_category}"', extinf_line, flags=re.IGNORECASE)
                                else:
                                    # Jika dari sananya tidak ada group-title, kita suntikkan secara paksa
                                    if ',' in extinf_line:
                                        parts = extinf_line.split(',', 1)
                                        extinf_line = f'{parts[0]} group-title="{target_category}",{parts[1]}'
                                    else:
                                        extinf_line = f'{extinf_line} group-title="{target_category}"'
                                
                                current_block[0] = extinf_line
                                
                                # 2. Timpa baris #EXTGRP (jika ada di dalam blok)
                                for idx in range(1, len(current_block)):
                                    if current_block[idx].upper().startswith("#EXTGRP:"):
                                        current_block[idx] = f"#EXTGRP:{target_category}"
                                
                                # Masukkan URL dan gabungkan ke output
                                current_block.append(stream_url) 
                                filtered_lines.extend(current_block) 
                                total_entries += 1
                                
                        current_block = []
                        current_extinf = ""
                        
        except requests.exceptions.RequestException as e:
            print(f"  > WARNING: Gagal memproses {url}. Error: {e}")
            continue
            
    print(f"Total {total_entries} saluran difilter menjadi grup [{target_category}].")
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write('\n'.join(filtered_lines) + '\n')
    print(f"Playlist [{output_file}] berhasil disimpan.")

# ====================================================================
# III. EKSEKUSI
# ====================================================================

if __name__ == "__main__":
    print("Memulai Multi-Filter M3U (Auto-Grouping/Overwrite)...")
    for config in CONFIGURATIONS:
        filter_m3u_by_config(config)
    print("\nProses selesai. Menu M3U sekarang bersih dan seragam!")
