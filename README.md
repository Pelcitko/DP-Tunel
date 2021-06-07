Vodárenský přivaděč Bedřichov
=============================

> Zveřejněno pro účely obhajoby

*   dostupné z [bedrichov2.tul.cz](http://bedrichov2.tul.cz/) (alternativa k původní aplikaci [bedrichov.tul.cz/Tunel](http://bedrichov.tul.cz/Tunel/))
*   přihlásit se pro volné procházení webu, je možné pod údaji _zajimame/mereni_

  

### Přepočty hodnot

1.  fáze:
    *   implementace beze změn v databázi
    *   přepočty se prováděli až před zobrazením
2.  fáze:
    *   vkládají se přepočtené hodnoty (pomocí _before triggeru_)
    *   již uložené hodnoty je možné přepočíst uživatelsky vyvolanou akcí v administračním rozhraní

  

### Uživatelské rozhraní

Jedná se o silně modifikovaný wrapper nad databází.

Jeho výhody jsou (z hlediska programátora/správce serveru):

*   programová přizpůsobitelnost,
*   automatizování základních potřeb programátora.

######   

Pro uživatele jsou hlavními stránkami, se kterými bude pracovat, stránka se zobrazením [všech dat](http://bedrichov2.tul.cz/mybox/data/?time__range__gte=2021-05-29) a [všech senzorů](http://bedrichov2.tul.cz/mybox/sensor/). Obě umožnují zobrazení grafu, po vyfiltrování pouze jednoho konkrétního senzoru.

#### Filtrování

Filtrování (omezení zobrazených hodnot) je umožněno v pravém sloupci rozhraní. Obsah zde umístěných filtrů je generován z databáze. Mezi jednotlivými filtry je možné chápat logické AND, tedy všechny použité filtry platí zároveň.

(Oproti původnímu řešením je možné dospět rychleji k cíli zadáním přímo zvoleného senzoru, např. jeho ID, nebo části textu v poznámce. Vyhledávací pole je implementováno s dynamicky načítanými hodnotami a funkcí _našeptávače_.)

#### Zobrazení grafu

Graf se zobrazí pouze pro jeden konkrétní senzor. V tuto chvíli nelze zobrazovat více grafů, pro více senzorů současně. Výhodou webového prostředí je, že uživatel může libovolně využívat možnosti internetového prohlížeče, a tedy také zobrazení webu na víc kartách/oknech.

  

Příklady grafů (s již přepočtenými historickými hodnotami):

*   [bedrichov2.tul.cz/mybox/data/?id\_sensor\_\_pk\_\_exact=187](http://bedrichov2.tul.cz/mybox/data/?id_sensor__pk__exact=187)
*   [bedrichov2.tul.cz/mybox/data/?id\_sensor\_\_pk\_\_exact=176&time\_\_range\_\_gte=01.01.2019&time\_\_range\_\_lte=01.01.2020](http://bedrichov2.tul.cz/mybox/data/?id_sensor__pk__exact=176&time__range__gte=01.01.2019&time__range__lte=01.01.2020)
*   [bedrichov2.tul.cz/mybox/data/?id\_sensor\_\_pk\_\_exact=172&time\_\_range\_\_gte=1.01.2019&time\_\_range\_\_lte=1.01.2020](http://bedrichov2.tul.cz/mybox/data/?id_sensor__pk__exact=172&time__range__gte=1.01.2019&time__range__lte=1.01.2020)

  

  

* * *

Přílohy
-------

### Databáze

*   Popis postupu při [upgradu z PostgreSQL 9 -> 13](https://github.com/Pelcitko/DP-Tunel/blob/main/p%C5%99%C3%ADlohy/upgrade.md).
*   Vytvořený [trigger a obslužné funkce](https://github.com/Pelcitko/DP-Tunel/blob/main/p%C5%99%C3%ADlohy/calculate_trigger.sql).
*   Vytvořené [indexy](https://github.com/Pelcitko/DP-Tunel/blob/main/p%C5%99%C3%ADlohy/idxs.sql).

### Přepočty hodnot

*   [Tabulka vzorců s příslušnými senzory](https://docs.google.com/spreadsheets/d/e/2PACX-1vTkL6qh3izQO-4AbayzVSkE7lerUQrdSawkYdSuioanF6Tq7KWEQ-sT9dfQvvlGeqHmZDbz0adOg2yX/pubhtml?gid=424239906&single=true).
*   Popis přepočtů byl součástí [magisterského projektu](https://github.com/Pelcitko/DP-Tunel/blob/main/DP%20a%20MP/MP_Lukas_Pelc_Privadec_Bedrichov.pdf) (viz kapitola 2.2).

### Měření výkonu

*   [publikované grafy](https://docs.google.com/spreadsheets/d/e/2PACX-1vTkL6qh3izQO-4AbayzVSkE7lerUQrdSawkYdSuioanF6Tq7KWEQ-sT9dfQvvlGeqHmZDbz0adOg2yX/pubhtml?gid=1185949406&single=true)
*   [celý dokument](https://docs.google.com/spreadsheets/d/1oHWLO_D2KDMtN1XBKx3Qan8OIYeB_fAyHXkHfcsYUjE/edit?usp=sharing) s měřenými hodnotami
