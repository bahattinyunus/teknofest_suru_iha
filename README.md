<div align="center">

# 🚁 TEKNOFEST SÜRÜ ZEKASI KOMUTA MERKEZİ
### Sürü İHA (Swarm UAV) Yarışması 2025

![Sürü Komuta Merkezi](visionary_swarm_banner.png)

[![Lisans](https://img.shields.io/badge/LISANS-MIT-00E5FF?style=for-the-badge&logo=open-source-initiative&logoColor=white)](LICENSE)
[![Sürüm](https://img.shields.io/badge/SURUM-v1.3.0-00E5FF?style=for-the-badge&logo=git&logoColor=white)](CHANGELOG.md)
[![Testler](https://img.shields.io/badge/TESTLER-19%20GECTI-00E5FF?style=for-the-badge&logo=pytest&logoColor=white)](.github/workflows/ci.yml)
[![Durum](https://img.shields.io/badge/SISTEM-OPERASYONEL-00E5FF?style=for-the-badge&logo=ros&logoColor=white)](https://github.com/bahattinyunus/teknofest_suru_iha)
[![Çerçeve](https://img.shields.io/badge/CEKIRDEK-ROS2_HUMBLE-00E5FF?style=for-the-badge&logo=ros&logoColor=white)](https://docs.ros.org/en/humble/)
[![Simülasyon](https://img.shields.io/badge/SIM-GAZEBO-00E5FF?style=for-the-badge&logo=gazebo&logoColor=white)](https://gazebosim.org/)
[![Konteyner](https://img.shields.io/badge/KONTEYNER-DOCKER-00E5FF?style=for-the-badge&logo=docker&logoColor=white)](Dockerfile)

</div>

---

## 🌍 Küresel Sürü Zekası Ekosistemi
**"Dünyadaki Benzer Yarışmalar, Araştırma Laboratuvarları ve Açık Kaynak Projeler"**

Bu proje, küresel sürü robotatiği topluluğunun bir parçasıdır. Aşağıda, dünya çapındaki önemli kaynaklar kategorize edilerek listelenmiştir:

### 🏆 Prestijli Yarışmalar (Global Competitions)
| Yarışma / Organizasyon | Ülke / Bölge | GitHub Repo / Kaynak Kod |
| :--- | :--- | :--- |
| **MBZIRC Maritime Grand Challenge** | BAE | 🔗 [osrf/mbzirc](https://github.com/osrf/mbzirc) |
| **DARPA OFFSET (Swarm Experiment)** | ABD | 🔗 [niwcpac/mole](https://github.com/niwcpac/mole) |
| **IARC (International Aerial Robotics)** | Küresel | 🔗 [ICRS/IARC](https://github.com/ICRS/IARC) |
| **IMAV (Int. Micro Air Vehicle)** | Küresel | 🔗 [imav2022_nanocopter](https://github.com/tristandijkstra/imav2022) |
| **Swarm-UAV Competition** | Küresel | 🔗 [okantorun/Swarm-UAV](https://github.com/okantorun/Swarm-UAV) |
| **Swarm-Rescue (Search & Rescue)** | Küresel | 🔗 [ArkhamKnightGPC/drone-swarm-psc](https://github.com/ArkhamKnightGPC/drone-swarm-psc) |
| **CopterHack (Swarm-in-Blocks)** | Küresel | 🔗 [swarm-in-blocks](https://github.com/intelligent-soft-robotics/swarm-in-blocks) |

### 🔬 Akademik Araştırma Laboratuvarları (Research Labs)
| Laboratuvar / Proje | Kurum | Odak Alanı / Repo |
| :--- | :--- | :--- |
| **GRASP Lab** | UPenn | 🔗 [Multi-Robot Systems](https://github.com/grasp-irl) |
| **HeRoLab** | University of Georgia | 🔗 [heroswarmv2](https://github.com/herolab-uga/heroswarmv2) |
| **Swarm Lab** | UC Berkeley | 🔗 [Open Source Swarms](https://theswarmlab.com/) |
| **Marine Robotics Group** | MIT | 🔗 [The Thoroughbreds](https://github.com/MarineRoboticsGroup/SwarmRobot) |

### 💻 Açık Kaynak Sürü Yazılımları (Open Source Software)
| Proje İsmi | Tip | GitHub Link |
| :--- | :--- | :--- |
| **Awesome Swarm Drones** | Kürasyon | 🔗 [awesome-swarm-drones](https://github.com/awesomelistsio/awesome-swarm-drones) |
| **SwarmJS** | Simülatör | 🔗 [m-abdulhak/SwarmJS](https://github.com/m-abdulhak/SwarmJS) |
| **pyswarming** | Araç Seti | 🔗 [mrsonandrade/pyswarming](https://github.com/mrsonandrade/pyswarming) |
| **RoboMaster TT Swarm** | SDK / Driver | 🔗 [tianbot/rmtt_ros](https://github.com/tianbot/rmtt_ros) |
| **Crazyflie Firmware** | Firmware | 🔗 [bitcraze/crazyflie-firmware](https://github.com/bitcraze/crazyflie-firmware) |

### 📊 Teknik Karşılaştırma ve Rakip Analizi (Technical Benchmarking)
Sürü sistemleri, kullanım amacı ve teknoloji yığınına göre üç ana segmente ayrılmaktadır:

| Özellik | **Düşük Maliyetli / Eğitim** (Tello/RoboMaster) | **Yüksek Hassasiyetli / Ar-Ge** (Crazyflie/Crazyswarm) | **Endüstriyel / Karmaşık Görev** (PX4/MAVSDK) |
| :--- | :--- | :--- | :--- |
| **Donanım Platformu** | DJI Tello Talent (ESP32) | Bitcraze Crazyflie (STM32) | Pixhawk / Custom UAV |
| **Lokalizasyon** | ToF Sinyal / Wi-Fi | Motion Capture / Lighthouse | GPS / RTK / Vision-based |
| **Kontrol Mimarisi** | Merkezi (Station Mode) | Merkezi/Dağıtık (ROS) | Dağıtık (MAVLink/DDS) |
| **Simülasyon** | Gazebo / DroneBlocks | Crazyswarm Simulator | Gazebo / AirSim / SITL |
| **Öne Çıkan Gücü** | Kolay Kurulum / Blok Kodlama | İç Mekan Hassasiyeti (mm bazlı) | Ölçeklenebilirlik / Dış Mekan |

### 💡 Yeni Nesil Sürü Algoritmaları (SOTA Algorithms)
Rakiplerin ve global projelerin kullandığı en güncel Sürü Zekası yaklaşımları:

1.  **Bio-inspired Flocking**: Reynolds' Boids (Ayrılma, Hizalanma, Birleşme) algoritmalarının gelişmiş versiyonları.
2.  **Decentralized Coordination (MANET)**: Merkezi bir lider olmadan, İHA'lar arası doğrudan veri alışverişi (Mesh Net).
3.  **Autonomous Reallocation**: Bir İHA devre dışı kaldığında, sürünün otomatik olarak formasyonunu ve görevini güncellemesi.
4.  **Neural Swarm Networks**: Karmaşık çevresel engellerden kaçınmak için derin pekiştirmeli öğrenme (DRL) tabanlı navigasyon.
5.  **Stigmergy-based Search**: Böceklerin feromon bırakma davranışından esinlenen alan tarama algoritmaları.

### 🎯 Global Standartlar ve Performans Metrikleri (KPIs)
Projemiz, **DARPA OFFSET** ve **MBZIRC** gibi üst düzey yarışmaların belirlediği global başarı kriterleri ile uyumlu olarak geliştirilmektedir:

| Metrik Grubu | KPI Tanımı | Hedef / Standart |
| :--- | :--- | :--- |
| **Operasyonel Verim** | **Exploration Ratio (Alan Tarama)** | %95+ kapsama kapasitesi |
| **Sürü Dayanıklılığı** | **Robustness (Sağlamlık)** | %25 araç kaybında dahi görev devamlılığı |
| **Hız ve Yanıt** | **Convergence Time** | Görev hedefine kilitlenme süresinin optimizasyonu |
| **İletişim** | **Bandwidth Efficiency** | Minimum veri yükü ile maksimum koordinasyon |
| **Otonomi** | **Decision Latency** | Dinamik engellere karşı <500ms tepki süresi |

### 🌍 Global Hizalanma (International Alignment)
- **Framework Uyumluluğu**: ROS 2 ve MAVLink standartlarında tam uyumluluk.
- **Modülerlik**: DARPA'nın "Agile Sprints" metodolojisine benzer hızlı prototipleme mimarisi.
- **Denial-Resilience**: GNSS-denied (GPS'siz) ortamlarda otonom navigasyon hedefleri.

### 📐 Matematiksel Temeller (Mathematical Foundations)
Sürü koordinasyonu, grafik teorisi ve dinamik sistemlerin birleşimine dayanır:

1.  **Laplacian Konsensüs**: İHA'lar arası durum (konum/hız) anlaşması:
    $$\dot{x}_i = - \sum_{j \in N_i} a_{ij} (x_i - x_j)$$
    *Burada $L = D - A$ (Laplacian Matrisi), sistemin yakınsama hızını ve kararlılığını belirler.*

2.  **Yapay Potansiyel Alanları (APF)**:
    - **Cezbedici Güç ($U_{att}$)**: Hedefe yönelim.
    - **İtici Güç ($U_{rep}$)**: Engel ve İHA arası çarpışma önleme.
    $$F_{total} = -\nabla U_{att} - \nabla U_{rep}$$

### 🛡️ Siber-Fiziksel Güvenlik (Cyber-Physical Security)
Elektronik Harp (EW) koşullarında sürünün operasyonel sürekliliği için uygulanan stratejiler:

- **GNSS Spoofing & Teleportation Tespiti**: Kinematik kısıt kontrolü (anlık hız > 25 m/s veya irtifa limit dışı durumları).
- **Byzantine Fault Isolation**: Sürü içindeki sahtelenmiş ("malicious") düğümlerin, konsensüs dışı hareketlerinden otomatik tespiti ve sürüden dışlanması.
- **Autonomous Fail-Safe**: Haberleşme karartması durumunda otomatik **Return-to-Launch (RTL)** geçişi.

### 📡 Haberleşme Mimarisi: MAVLink 2 vs DDS
Sistemimiz, hibrit bir haberleşme katmanı kullanmaktadır:

| Özellik | **MAVLink 2** | **ROS 2 (DDS)** |
| :--- | :--- | :--- |
| **Kullanım** | Telemetri & Düşük Seviye Komut | Dağıtık İşlem & Sensör Paylaşımı |
| **Güvenlik** | Message Signing (HMAC-SHA256) | TLS/DTLS Encryption |
| **Verimlilik** | Yüksek (Minimal Overhead) | Esnek (High Throughput) |
| **Kritiklik** | Real-time Kontrol Döngüsü | Üst Seviye Görev Planlama |

### 📈 Sürdürülebilirlik & İş Modeli (Business Model)
Projemiz sadece teknik bir başarı değil, aynı zamanda ticarileşme potansiyeli yüksek bir girişimdir:

#### **SWOT Analizi**
| **Güçlü Yönler (S)** | **Zayıf Yönler (W)** |
| :--- | :--- |
| Hibrit haberleşme katmanı (MAVLink+DDS) | Yüksek donanım maliyetleri |
| Gelişmiş siber-güvenlik protokolleri & IDS | GPS bağımlılığı (şimdilik) |
| **Fırsatlar (O)** | **Tehditler (T)** |
| Teknofest Girişim Programı desteği | Hızlı teknolojik eskime |
| Genişleyen otonom tarım ve lojistik pazarı | Değişen UAV regülasyonları |

#### **Değer Önerisi (Value Proposition)**
- **Decentralized Reliability**: Tek bir İHA kaybında dahi operasyonu durdurmayan otonom yapı.
- **Security-First**: Sinyal karıştırma ve sahteciliğe karşı entegre savunma.
- **Scalable Framework**: 10'dan 100'e kadar İHA'yı destekleyen esnek mimari.

---

## 🌐 Görev Tanımı
**"Uçuşta Birlik, Sayılarda Zeka"**

Bu depo, **Teknofest Sürü İHA Yarışması** için tasarlanmış **Elit Sürü Zekası Sistemi**ni barındırır. Otonom drone koordinasyonu, formasyon uçuşu ve görev icrası için gelişmiş merkeziyetsiz algoritmalar uygular.

### 🧠 Nöral Sürü Ağı
Sistemimiz, biyolojik sürü davranışlarını taklit eden yapay sinir ağları ile güçlendirilmiştir. Her bir İHA, çevresini algılar ve sürünün geri kalanıyla gerçek zamanlı veri paylaşır.

![Nöral Ağ Görselleştirmesi](swarm_neural_network_viz.png)

---

Her bir sürü elemanı, yüksek manevra kabiliyetine sahip, sensör füzyonu ile donatılmış özel bir İHA prototipidir.

| Bileşen | Model / Teknik Özellik | Rol / Görev |
| :--- | :--- | :--- |
| **Uçuş Kontrolcü** | Orange Cube+ (OrangeBox) | Real-time stabilizasyon & MAVLink |
| **Tamamlayıcı Bilgisayar** | NVIDIA Jetson Orin Nano | Sürü zekası, SLAM & Obje Tespiti |
| **Haberleşme Modülü** | Herelink Blue / RFD900x | Uzun menzilli Mesh veri linki |
| **Konumlandırma** | Here3+ RTK GPS / Optical Flow | Santimetrik hassasiyette konumlandırma |
| **Güç Sistemi** | 4S/6S LiPo + T-Motor Ecosystem | Endüstriyel verimlilik & güç yönetimi |
| **Sensör Füzyonu** | RPLIDAR A3 + Depth Camera | Dinamik engel kaçınma & 3D Haritalama |

![Drone Teknik Şeması](drone_blueprint_schematic.png)

---

## 🏗️ Sistem Mimarisi: KOVAN (THE HIVE)

Sistem, düğüm arızalarına ve dinamik çevresel değişikliklere karşı dayanıklı, **Merkeziyetsiz Lider-Takipçi** mimarisi üzerinde çalışır.

```mermaid
graph TD
    A[Görev Kontrol] -->|Talimatlar| B(Sürü Lideri)
    B -->|Koordinasyon| C(Takipçi 1)
    B -->|Koordinasyon| D(Takipçi 2)
    B -->|Koordinasyon| E(Takipçi 3)
    C <-->|Mesh Ağı| D
    D <-->|Mesh Ağı| E
    E <-->|Mesh Ağı| C
    
    style A fill:#1a1a1a,stroke:#00E5FF,stroke-width:2px,color:#fff
    style B fill:#003366,stroke:#00E5FF,stroke-width:2px,color:#fff
    style C fill:#001a33,stroke:#00E5FF,stroke-width:1px,color:#ccc
    style D fill:#001a33,stroke:#00E5FF,stroke-width:1px,color:#ccc
    style E fill:#001a33,stroke:#00E5FF,stroke-width:1px,color:#ccc
```

### 🔹 Çekirdek Modüller
| Modül | Dosya / Dizin | Protokol / Görev | Durum |
| :--- | :--- | :--- | :--- |
| **Algoritmik Motor** | `swarm_core/algorithms.py` | Boids, Formasyon, APF, SAR & IDS Motoru | 🟢 **AKTİF** |
| **Komuta Düğümü** | `swarm_core/node_commander.py` | ROS 2 Çoklu İHA Otonom Seyrüsefer | 🟢 **AKTİF** |
| **Canlı Telemetri** | `swarm_core/dashboard.py` | Terminal Tabanlı Kütle Merkezi & Dağılım İzleme | 🟢 **AKTİF** |
| **Görev Analizi** | `swarm_core/analyze_mission.py` | Post-Process KPI, Markdown & JSON Raporlama | 🟢 **AKTİF** |
| **Simülasyon** | `src/swarm_simulation` | Gazebo Çoklu İHA Dünyası & Başlatma Dosyaları | 🟢 **AKTİF** |
| **Sürekli Entegrasyon** | `.github/workflows/` | Pytest (19/19 Test) & ROS 2 Humble CI | 🟢 **AKTİF** |

---

### 🗺️ Geliştirme Yol Haritası (Roadmap)

```mermaid
flowchart LR
    subgraph S1["Faz 1: Hazırlık & Ar-Ge"]
        A["Mimari & Matematiksel Modelleme"] --> B["Sürü Çekirdek Algoritmaları"]
    end
    subgraph S2["Faz 2: Teknofest 2025"]
        C["Gazebo & SITL Entegrasyonu"] --> D["Saha Testleri & Görev İcrası"]
    end
    subgraph S3["Faz 3: Swarm-to-Swarm (2026)"]
        E["Heterojen Sürü İşbirliği"] --> F["Dinamik Ad-Hoc Mesh Ağı"]
    end
    subgraph S4["Faz 4: Tam Otonomi (2027)"]
        G["Kendi Kendini İyileştiren Sürü & Uç Zeka"]
    end
    B --> C
    D --> E
    F --> G
```

---

## 🛠️ Teknolojik Cephanelik

**Komuta Merkezi**, hassasiyet ve güvenilirliği sağlamak için son teknoloji bir yığın kullanır.

- **İşletim Sistemi**: Ubuntu 22.04 LTS (Jammy Jellyfish) / Windows 11 WSL2
- **Ara Katman**: ROS 2 Humble Hawksbill
- **Simülasyon**: Gazebo Garden / Classic
- **Uçuş Kontrol**: PX4 Autopilot / ArduPilot
- **Konteynerizasyon**: Docker & Docker Compose
- **Test ve Kalite**: Pytest (19 Birim Testi), Flake8 Linting

---

## 🚀 Kurulum Protokolleri

### ⚡ Hızlı Başlangıç (Docker)
Sürü Simülasyonunu konteynerize edilmiş bir ortamda başlatın:

```bash
# Depoyu klonlayın
git clone https://github.com/bahattinyunus/teknofest_suru_iha.git

# Komuta Merkezine girin
cd teknofest_suru_iha

# Sürüyü konuşlandırın
docker-compose up --build
```

### 🔧 Manuel Kurulum (Yerel ROS 2)
Gerekli Python ve ROS bağımlılıklarını yükleyin:
```bash
# Python bağımlılıklarını kurun
pip install -r requirements.txt

# ROS 2 çalışma alanını derleyin
colcon build --symlink-install

# Ortamı kaynak gösterin
source install/setup.bash

# Sürü Komuta filosunu başlatın
ros2 launch swarm_core swarm.launch.py num_drones:=5 formation_type:=V_SHAPE mission_mode:=BOIDS
```

### 🛰️ Görev Modları (Mission Modes)
Sürü, 5 farklı operasyonel mod arasında dinamik olarak geçiş yapabilir:

1. **`BOIDS`**: Reynolds Flocking (Ayrılma, Hizalanma, Birleşme ve Hedef Çekimi).
2. **`FORMATION`**: Lider-Takipçi formasyon uçuşu. Desteklenen geometriler:
   - `V_SHAPE` (V Formasyonu)
   - `LINE` (Yan Yana Hat Formasyonu)
   - `COLUMN` (Arka Arkaya Kolon Formasyonu)
   - `CIRCLE` (Çevre Koruma Çemberi)
   - `GRID` (2D Matris Formasyonu)
3. **`SEARCH`**: Arama-Kurtarma için Arşimet Spirali (`SPIRAL`) veya Lawnmower (`LAWNMOWER`) taraması.
4. **`APF`**: LiDAR ve mesafe sensörü destekli Yapay Potansiyel Alanı ile engel sakınımı.
5. **`RTL`**: İletişim kopmasında veya düşük bataryada otonom üsse dönüş (Fail-Safe).

*Çalışma anında görev modu değiştirme:*
```bash
ros2 param set /drone_1/swarm_commander_1 mission_mode FORMATION
ros2 param set /drone_1/swarm_commander_1 formation_type V_SHAPE
```

### 🖥️ Canlı Telemetri Paneli (Command Dashboard)
Sürüdeki tüm İHA'ların anlık konumlarını, kütle merkezini, dağılım yarıçapını ve güvenlik durumunu izlemek için:
```bash
ros2 run swarm_core dashboard
```

### 📊 Görev Sonrası Analiz & Raporlama (Post-Mission Analysis)
Görev sırasında kaydedilen JSON telemetri verisini analiz edip profesyonel Markdown veya JSON raporu üretin:
```bash
python3 src/swarm_core/swarm_core/analyze_mission.py mission_log_drone_1_*.json \
    --report gorev_raporu.md \
    --export-summary ozet.json
```

---

## 🧪 Birim Testleri & Kalite Güvencesi
Algoritmalar ve komuta mantığı 19 kapsamlı birim testi ile doğrulanmaktadır:
```bash
pytest -v
```

---

## 👨‍✈️ Amiral & Mimar

<div align="center">

| **Bahattin Yunus Çetin** |
| :---: |
| **BT Mimarı | Trabzon, Türkiye** |
| 🎓 *Sürü Zekası Ağının Vizyoneri* |
| 🔗 [GitHub](https://github.com/bahattinyunus) • [LinkedIn](https://linkedin.com/in/bahattinyunus) |

</div>

---

## 🤝 Sürüye Katıl
Kovan her zaman genişliyor. **Kolektif Zeka**ya katkıda bulunmak istiyorsanız, lütfen protokollerimize bakın.

- **[CONTRIBUTING.md](CONTRIBUTING.md)**: Kod gönderme protokolü.
- **[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)**: Etkileşim kuralları.

---

<div align="center">

*"Bütün, parçaların toplamından daha büyüktür."*  
**© 2025 Teknofest Sürü İHA Takımı. Tüm Sistemler Çevrimiçi.**

</div>
<p align="center">
  <img src="https://img.shields.io/badge/Powered%20By-TEKNOFEST-red?style=for-the-badge&logo=rocket&logoColor=white" alt="TEKNOFEST Support">
</p>
