Použití modulu
==============
V dokumentaci zatím bylo uvedeno jak modul nainstalovat a jak použít jednotlivé
vrstvy API, které poskytuje.

Nyní se zaměřím na poslední část, kterou je nutné popsat - jakým způsobem
vlastně uživatel Edepositu může tento modul využívat.

Motivace
--------
Mnoho uživatelů bude pravděpodobně řešit jako první otázku motivace: „Proč bych
vlastně měl modul používat?“

Odpověď je jednoduchá - protože může ušetřit spoustu času a práce. Data nahraná
přes FTP jsou automaticky párována s metadaty, můžete používat dávkové nahrávání
a celé to vyžaduje jen pár kroků, na rozdíl od webového rozhraní.

Pokud chcete, celý proces se dá zautomatizovat, takže se dá s trochou nadsázky
říct, že na něj můžete zapomenout.

Použití
=======

Krok 1: Konfigurace
-------------------
Předtím než můžete FTP rozhraní začít používat je zapotřebí povolit přístup a
nastavit heslo. To můžete provést na webových stránkách Edepositu.

.. TODO: doplnit odkaz na edeposit
.. TODO: Screenshoty jak to má vypadat.

Krok 2: Připojení na FTP
------------------------
Poté co nastavíte nezbytné údaje z `Kroku 1` se můžete zkusit připojit k FTP
serveru.

Doporučený FTP klient pro připojení je FileZilla_, ale nic vám nebrání použít
jakéhokoliv klienta, kterého máte k dispozici.

.. _FileZilla: https://filezilla-project.org/

.. image:: /_static/filezilla.png
    :width: 400px

Následující ukázky využívají pro připojení FTP klient `caja`, který je k
dispozici v distribuci `Linux Mint <http://www.linuxmint.com/>`_. Podobným
způsobem je možné použít i Explorer z Windows, který Vám umožní připojit se na
server napsáním adresy ve tvaru ``ftp://uzivatel@adresa`` do adresního řádku.

.. image:: /_static/explorer.png
    :width: 400px

Poté co se připojíte na server si pravděpodobně všimnete, že je zde již přítomen
jeden soubor, pojmenovaný ``delete_me_to_import_files.txt``. Pokud tento soubor
smažete, nic se nestane a soubor se na serveru opět objeví.

.. image:: /_static/lock.gif
    :width: 400px

Smysl tohoto souboru je vysvětlen dále v textu, prozatím ho můžete ignorovat.

Krok 3: Párování dat
--------------------
Tento modul Vám umožňuje automaticky párovat soubory `ebooků` s `metadaty`. Tyto
`páry` jsou rozpoznány a brány jako jeden celek ve webovém rozhraní Edepositu,
takže později již nemusíte ručně vyplňovat povinné informace.

`Pár` je vždy složen z dvojice `metadatového` souboru a souboru `eknihy`. `Pár`
je možné vytvořit třemi různými způsoby:

- Dva libovolně pojmenované soubory ve složce, která obsahuje jen tyto dva
  soubory a nic jiného.
- Dva stejně pojmenované soubory v jedné složce. Jméno může souborů být
  libovolné, důležité je aby bylo až na příponu souborů stejné (například
  ``babicka.json`` a ``babicka.pdf``). Složka může obsahovat libovolný počet
  dalších, odlišně pojmenovaných souborů, či `párů`.
- Dva soubory pojmenované jako jedno validní ISBN, ať již jsou v adresářové
  struktuře  umístěny kdekoliv. Například ``/metadata/80-86056-31-7.json`` a
  ``/ebooky/80-86056-31-7.pdf``.

Všechny tři metody automatického párování metadat mohou být vypnuty v nastavení
FTP serveru ve Vašem účtu.

Krok 4: Spuštění importu
------------------------
Import je spuštěn smazáním již zmíněného `zamykacího` souboru
``delete_me_to_import_files.txt``.

Spouštění importu mazáním `zámkového` souboru bylo zvoleno, protože neexistuje
žádný spolehlivý a obecně použitelný způsob, jak poznat, že již byl soubor
skutečně celý přenesen a zda došlo k nahrání všech zamýšlených souborů.
Někteří FTP klienti totiž otevírají a zavírají vícero spojení a běžně se
vyskytují situace, kdy přenos souboru je náhle přerušen a pokračování probíhá o
několik vteřin či minut později v jiném spojení.

.. image:: /_static/import.gif
    :width: 400px

Protokol importu a chyb
-----------------------
Jak je možné vidět na předešlé animaci, poté co byly nahrány soubory a spuštěn
import došlo na serveru k opětovnému vytvoření `zámkového` souboru. Navíc se
zde také objevil soubor ``import.log.txt``.

Tento soubor obsahuje podrobné informace o právě proběhlém importu souborů.
Na první řádce se nachází hlášení ``Status: Ok``, či ``Status: Error``, v
závislosti na úspěchu procesu importu. Dále pak následují podrobná hlášení
o zpracování jednotlivých souborů.

Díky tomu je možné jednoduše implementovat scripty, které budou automaticky
nahrávat Vámi zvolená data na server.

Pokud není možné přečíst či zpracovat soubory metadat, je vytvořen navíc také
soubor ``error.log.txt``, který obsahuje seznam chyb a chybné soubory jsou
ponechány na serveru, aby je bylo možné opravit.

.. image:: /_static/error.gif
    :width: 400px

Toto chování je možné částečně změnit v nastavení.

Metadata
--------
Každý datový soubor e-knih by měl mít k sobě přiložen i soubor metadat. Nejedná
se o povinnost, pouze o snahu ušetřit námahu s pozdějším ručním přidáváním dat
ve webovém rozhraní.

Momentálně existuje podpora pro čtyři typy `metadatových` souborů:

- :doc:`JSON </api/ftp.decoders.parser_json>`
- :doc:`CSV </api/ftp.decoders.parser_csv>`
- :doc:`XML </api/ftp.decoders.parser_xml>`
- :doc:`YAML </api/ftp.decoders.parser_yaml>`

Soubory metadat jsou rozeznávány podle jejich přípony - ``.json`` pro JSON
soubory, ``.csv`` pro CSV, ``.xml`` pro XML a ``.yaml`` pro YAML soubory.

Varování: **Všechny metadatové soubory jsou očekávány v kódování UTF-8!**

Každý soubor metadat by měl obsahovat několik povinných a několik volitelných
polí. Popis a seznam všech polí je možné najít zde:

- :doc:`/workflow/pozadovane`

Pokud mají soubory špatnou strukturu, kódování či oprávnění pro přístup, tak
dochází k vytvoření souboru chybového protokolu a metadata jsou přeskočeny.