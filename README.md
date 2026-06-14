\# QMOOD Tabanlı Yazılım Kalitesi Analizi ve LLM Destekli Değerlendirme



\## Proje Adı



QMOOD Tabanlı Yazılım Kalitesi Analizi ve LLM Destekli Değerlendirme: picocli Örneği



\## Seçilen Açık Kaynak Proje



\- Proje: picocli

\- GitHub: https://github.com/remkop/picocli

\- Programlama dili: Java

\- Alan: Komut satırı arayüzü oluşturma ve argüman ayrıştırma kütüphanesi



\## İncelenen Sürümler



Bu çalışmada picocli projesinin aşağıdaki 10 sürümü analiz edilmiştir:



1\. v4.0.4

2\. v4.1.0

3\. v4.1.4

4\. v4.2.0

5\. v4.3.0

6\. v4.3.2

7\. v4.4.0

8\. v4.5.2

9\. v4.6.3

10\. v4.7.7



\## Kullanılan Araçlar



\- Git

\- Java JDK 21

\- CK Tool

\- Python

\- Pandas

\- NumPy

\- Matplotlib

\- Gemini

\- DeepSeek

\- Claude



\## Metrik Çıkarım Süreci



1\. picocli deposu klonlandı.

2\. Seçilen 10 sürüm Git etiketleri üzerinden ayrı klasörlere çıkarıldı.

3\. Her sürüm için `src/main/java` klasörü CK Tool ile analiz edildi.

4\. CK Tool tarafından üretilen `class.csv` ve `method.csv` dosyaları `data/raw\_metrics/` altında saklandı.

5\. Sürüm bazlı özet metrikler hesaplandı.

6\. QMOOD tasarım özellikleri ve kalite nitelikleri türetildi.

7\. Tüm kalite skorları referans sürüm olan `v4.0.4` değerlerine göre normalize edildi.

8\. Son sürüm olan `v4.7.7` için sınıf düzeyinde risk analizi yapıldı.



\## Kullanılan Metrikler



\- WMC

\- DIT

\- CBO

\- RFC

\- LCOM

\- NOM

\- DAM

\- Class Count

\- Method Count



\## QMOOD Hesaplama Yöntemi



QMOOD kapsamında aşağıdaki kalite nitelikleri hesaplanmıştır:



\- Reusability

\- Flexibility

\- Understandability

\- Functionality

\- Extendibility

\- Effectiveness



Toplam kalite indeksi şu şekilde hesaplanmıştır:



```text

TQI = Reusability + Flexibility + Understandability + Functionality + Extendibility + Effectiveness

```



Bu çalışmada QMOOD tasarım özellikleri CK Tool çıktılarından türetilmiştir. Bazı QMOOD metrikleri CK Tool tarafından doğrudan verilmediği için proxy metrikler kullanılmıştır. Örneğin cohesion için TCC değeri elde edilemediğinden LCOM tabanlı ters cohesion proxy kullanılmıştır.



\## LLM Değerlendirme Süreci



Elde edilen metrik ve QMOOD sonuçları üç farklı LLM modeline verilmiştir:



\- Gemini

\- DeepSeek

\- Claude



LLM modellerinden aşağıdaki başlıklarda yorum istenmiştir:



\- Genel kalite değerlendirmesi

\- Bakım yapılabilirlik analizi

\- Teknik borç tahmini

\- Mimari kalite yorumu

\- Refactoring önerileri

\- Sınırlılıkların değerlendirilmesi



LLM cevapları aşağıdaki ölçütlere göre karşılaştırılmıştır:



\- Metriklere bağlılık

\- Teknik doğruluk

\- Refactoring önerisi kalitesi

\- Halüsinasyon riski

\- Sürüm trendini anlama

\- Sınırlılık farkındalığı



\## Klasör Yapısı



```text

qmood-picocli-github/

├── data/

│   ├── raw\_metrics/

│   ├── processed\_metrics/

│   └── qmood\_scores/

├── figures/

├── scripts/

├── prompts/

├── llm\_outputs/

├── report/

├── presentation/

├── notebooks/

├── README.md

└── .gitignore

```



\## Klasör Açıklamaları



| Klasör | Açıklama |

|---|---|

| `data/raw\_metrics/` | CK Tool tarafından üretilen ham `class.csv` ve `method.csv` dosyaları |

| `data/processed\_metrics/` | Sürüm bazlı özet metrikler ve riskli sınıf tabloları |

| `data/qmood\_scores/` | QMOOD kalite skoru çıktıları |

| `figures/` | Rapor ve sunumda kullanılan grafikler |

| `scripts/` | Metrik işleme, QMOOD hesaplama ve grafik üretim kodları |

| `prompts/` | LLM modellerine verilen prompt dosyaları |

| `llm\_outputs/` | Gemini, DeepSeek ve Claude çıktıları |

| `report/` | Teknik raporun Word ve PDF sürümleri |

| `presentation/` | Proje sunum dosyası |

| `notebooks/` | Varsa Jupyter Notebook çalışmaları |



\## Çalıştırma Komutları



\### CK Tool ile metrik çıkarımı



Aşağıdaki örnek komut `v4.7.7` sürümü içindir:



```powershell

$CK\_JAR = "repositories\\ck\\target\\ck-0.7.1-SNAPSHOT-jar-with-dependencies.jar"

$SOURCE\_PATH = "versions\\v4.7.7\\src\\main\\java"

$OUTPUT\_PATH = "data\\raw\_metrics\\v4.7.7"



New-Item -ItemType Directory -Force -Path $OUTPUT\_PATH | Out-Null

java -jar $CK\_JAR $SOURCE\_PATH false 0 false $OUTPUT\_PATH

```



\### QMOOD skorlarını hesaplama



```powershell

python scripts\\qmood\_calculation.py

```



\### Grafik üretimi



```powershell

python scripts\\generate\_figures.py

```



\### v4.7.7 riskli sınıf tablosunu çıkarma



```powershell

python scripts\\extract\_v477\_risky\_classes.py "data\\raw\_metrics\\v4.7.7\\class.csv" --out-dir "data\\processed\_metrics" --top 20

```



\## Temel Bulgular



\- Class count `192` değerinden `219` değerine yükselmiştir.

\- Method count `1517` değerinden `1848` değerine yükselmiştir.

\- TQI `4.0100` değerinden `4.1015` değerine yükselmiştir.

\- Reusability, Flexibility, Functionality ve Effectiveness değerleri artmıştır.

\- Understandability ve Extendibility değerleri gerilemiştir.

\- WMC, RFC ve LCOM metriklerindeki artış bakım yapılabilirlik açısından risk oluşturmuştur.

\- v4.7.7 sınıf düzeyi risk analizinde en riskli sınıfların çoğu `picocli.CommandLine` ve iç sınıfları çevresinde yoğunlaşmıştır.



\## Sınırlılıklar



\- QMOOD skorları referans sürüm olan `v4.0.4` değerlerine göre normalize edilmiştir.

\- Sonuçlar mutlak kalite değil, referans sürüme göre göreli kalite değişimini göstermektedir.

\- Bazı QMOOD tasarım özellikleri CK Tool çıktılarından doğrudan elde edilemediği için proxy metrikler kullanılmıştır.

\- Ortalama metrikler sınıf düzeyindeki aykırı değerleri gizleyebilir.

\- LLM yorumları nihai doğruluk kaynağı olarak değil, metrik tabanlı yorumlama desteği olarak değerlendirilmiştir.



\## Teslim İçeriği



Bu depoda aşağıdaki teslim çıktıları bulunmaktadır:



\- Teknik rapor

\- QMOOD hesaplama ve analiz kodları

\- Ham ve işlenmiş metrik dosyaları

\- Grafikler ve görselleştirmeler

\- Kullanılan promptlar

\- LLM model çıktıları

\- Riskli sınıf analizi

\- Sunum dosyası

