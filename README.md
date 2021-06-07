# README

  

Vodárenský přivaděč Bedřichov
=============================

  

> Zveřejněno pro účely obhajoby

*   dostupné z [bedrichov2.tul.cz](http://bedrichov2.tul.cz/)
*   přihlásit se pro volné procházení webu, je možné pod údaji _zajimame/mereni_

  

### Přepočty hodnot

1.  fáze:
    *   implementace beze změn v databázi
    *   přepočty se prováděli před zobrazením
2.  fáze:
    *   vkládají se přepočtené hodnoty (pomocí _before triggeru_)
    *   již uložené hodnoty je možné přepočíst uživatelsky vyvolanou akcí v administračním rozhraní

  

### Uživatelské rozhraní

Jedná se o silně modifikovaný wrapper nad databází.

Jeho výhody jsou:

*   snadném programové přizpůsobení,
*   automatizování základních potřeb programátora.

  

  

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