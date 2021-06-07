### Instalace PG13

> Pracuji jako obyčejný uživatel nad adresářem /opt/shared
> Záloha, hlavně pro pozdější kopírování nastavení:

```bash
sudo cp -r /opt/postgreSQL_DB/ ./postgreSQL_DB/
```

Podle návodu dokumentace: [postgresql.org/download/linux/redhat](https://www.postgresql.org/download/linux/redhat/)

```bash
# Install the repository RPM:
sudo yum install -y https://download.postgresql.org/pub/repos/yum/reporpms/EL-7-x86_64/pgdg-redhat-repo-latest.noarch.rpm

# Install PostgreSQL:
sudo yum install -y postgresql13-server
```

Návod selhal.

### Založení databáze

Dále najitá cesta:

```bash
sudo -u postgres /usr/pgsql-13/bin/initdb --locale=en_US.UTF-8 -D /opt/pgsql/13/data
pg_ctl -D /opt/postgreSQL_DB/ stop
sudo -u postgres /usr/pgsql-13/bin/pg_upgrade \
        -b /usr/bin/ \
        -B /usr/pgsql-13/bin/ \
        -d /opt/postgreSQL_DB/ \
        -D /var/lib/pgsql/13/data/ \
        --check
```

Chyba: Při spouštění zkušebního upgradu se vyskytuje problém s přejmenováním přepínače unix\_socket\_directory ⇒ unix\_socket\_directories

Řešeno pomocí podvrhnutí souboru: [postgresql - pg\_upgrade unrecognized configuration parameter "unix\_socket\_directory" - Database Administrators Stack Exchange](https://dba.stackexchange.com/questions/50135/pg-upgrade-unrecognized-configuration-parameter-unix-socket-directory/86929#86929)

```bash
mv /usr/bin/pg_ctl{,-orig}
echo '#!/bin/bash' > /usr/bin/pg_ctl
echo '"$0"-orig "${@/unix_socket_directory/unix_socket_directories}"' >> /usr/bin/pg_ctl
chmod +x /usr/bin/pg_ctl
# vrátit hack:
mv -f /usr/bin/pg_ctl{-orig,}
```

Chyba: Při spouštění zkušebního upgradu databáze odmítá spojení

```bash
vim /opt/postgreSQL_DB/pg_hba.conf
# byl zakomentovaný řádek 88: local   all  all  trust
sudo -u postgres pg_ctl -D /opt/postgreSQL_DB/ reload
```



```bash
sudo -u postgres /usr/pgsql-13/bin/pg_upgrade \
        -b /usr/bin/ \
        -B /usr/pgsql-13/bin/ \
        -d /opt/postgreSQL_DB/ \
        -D /var/lib/pgsql/13/data/ \
        --check
Performing Consistency Checks on Old Live Server
------------------------------------------------
Checking cluster versions                                   ok
Checking database user is the install user                  ok
Checking database connection settings                       ok
Checking for prepared transactions                          ok
Checking for reg* data types in user tables                 okChecking for contrib/isn with bigint-passing mismatch       ok
Checking for tables WITH OIDS                               fatal
Your installation contains tables declared WITH OIDS, which is not
supported anymore.  Consider removing the oid column using
    ALTER TABLE ... SET WITHOUT OIDS;
A list of tables with the problem is in the file:
    tables_with_oids.txt
Failure, exiting
```

Chyba: Při spouštění zkušebního upgradu nalezeny tabulky s OID

sudo cat tables\_with\_oids.txt

> In database: pst
> public.person
> In database: pstvit
> public.person

Definice problematické tabulky person:

```bash
-- Table: public.person


-- DROP TABLE public.person;
CREATE TABLE public.person
(
    id_person integer NOT NULL DEFAULT nextval(('seq_person'::text)::regclass),
    username character varying(64) COLLATE pg_catalog."default",
    userfullname character varying(128) COLLATE pg_catalog."default",
    email character varying(64) COLLATE pg_catalog."default",
    mobil character varying(20) COLLATE pg_catalog."default",
    id_usersys integer,
    usergroups integer[],
    useraftername character varying(32) COLLATE pg_catalog."default",
    userbeforename character varying(32) COLLATE pg_catalog."default",
    homepage character varying COLLATE pg_catalog."default",
    id_personleaders integer[],
    lastvisit timestamp without time zone,
    userpasswd character(35) COLLATE pg_catalog."default",
    CONSTRAINT person_pkey PRIMARY KEY (id_person)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;


ALTER TABLE public.person
    OWNER to rimnacm;


GRANT ALL ON TABLE public.person TO rimnacm;


GRANT SELECT ON TABLE public.person TO _measurement_prad
```

Oprava:

```bash
sudo -u postgres psql pst
psql (9.2.24)
pst=# ALTER TABLE public.person SET WITHOUT OIDS;
pst=# \q

lukas.pelc@pg-prod2.nti.tul.cz /opt/shared $ sudo -u postgres /usr/pgsql-13/bin/pg_upgrade -b /usr/bin/ -B /usr/pgsql-13/bin/ -d /opt/postgreSQL_DB/ -D /opt/pg
sql/13/data/ --check
Performing Consistency Checks on Old Live Server
------------------------------------------------
Checking cluster versions                                   ok
Checking database user is the install user                  ok
Checking database connection settings                       ok
Checking for prepared transactions                          ok
Checking for reg* data types in user tables                 ok
Checking for contrib/isn with bigint-passing mismatch       ok
Checking for tables WITH OIDS                               ok
Checking for invalid "sql_identifier" user columns          ok
Checking for invalid "unknown" user columns                 ok
Checking for hash indexes                                   ok
Checking for roles starting with "pg_"                      ok
Checking for incompatible "line" data type                  ok
Checking for presence of required libraries                 ok
Checking database user is the install user                  ok
Checking for prepared transactions                          ok
Checking for new cluster tablespace directories             ok


*Clusters are compatibl
```

Uff!



Chyba: Při spuštění bez --check dvaktát došlo místo a bylo nutné smazat init a požádosti na diskový prostor provést znovu.

```bash
sudo rm -rf /opt/pgsql/
sudo -u postgres /usr/pgsql-13/bin/initdb --locale=en_US.UTF-8 -D /opt/pgsql/13/data
sudo -u postgres /usr/pgsql-13/bin/pg_upgrade -b /usr/bin/ -B /usr/pgsql-13/bin/ -d /opt/postgreSQL_DB/ -D /opt/pgsql/13/data/
```

### Nyní je potřeba změnit konfigurační soubory

```bash
sudo -u postgres vim /opt/pgsql/13/data/pg_hba.conf
```

1.  Zakomentovat lokální spojení
2.  Přidat hosty podle původního vzoru pg\_hba.conf



```bash
lukas.pelc@pg-prod2.nti.tul.cz /opt/shared $ sudo -u postgres pg_ctl -D /opt/pgsql/13/data/ start
server starting
lukas.pelc@pg-prod2.nti.tul.cz /opt/shared $ LOG:  unrecognized configuration parameter "dynamic_shared_memory_type" in file "/opt/pgsql/13/data/postgresql.conf" line 142
LOG:  unrecognized configuration parameter "max_wal_size" in file "/opt/pgsql/13/data/postgresql.conf" line 228
LOG:  unrecognized configuration parameter "min_wal_size" in file "/opt/pgsql/13/data/postgresql.conf" line 229
FATAL:  configuration file "/opt/pgsql/13/data/postgresql.conf" contains errors
```

Ještě postgresql.conf

```bash
sudo -u postgres vim /opt/pgsql/13/data/postgresql.conf
```

Zde by si postgres možná zasloužil lepší nastavení. Nevím jaké jsou parametry serveru.

```bash
# https://pgtune.leopard.in.ua/#/
# DB Version: 13
# OS Type: linux
# DB Type: web
# Total Memory (RAM): 2 GB
# CPUs num: 2
# Data Storage: hdd

max_connections = 200
shared_buffers = 512MB
effective_cache_size = 1536MB
maintenance_work_mem = 128MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 4
effective_io_concurrency = 2
work_mem = 2621kB
min_wal_size = 1GB
max_wal_size = 4GB
max_worker_processes = 2
max_parallel_workers_per_gather = 1
max_parallel_workers = 2
max_parallel_maintenance_workers = 1
```