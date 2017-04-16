# 10 */3 * * *  su - postgres -c /home/backup/fcdb.bak.sh
10 */3 * * *    su - postgres -c /home/backup/tosnodb.bak.sh
30 5 * * 1,3,5  su - user -c /home/backup/tosnomedia.bak.sh
# 30 5 * * 1,3,5        su - fcpushkin -c /home/backup/fclubmedia.bak.sh
# 0 3 * * * su - postgres -c 'psql -d fcdb ' < /home/jobs/type_active.sql
0 3 * * * su - postgres -c 'psql -d fcmanager ' < /home/jobs/type_active.sql
0 5 * * * su - fcpushkin -c /home/fcmanager/crontab/contract_activate.py
0 4 * * * su - fcpushkin -c /home/fcmanager/crontab/price_activate.py


*******  /home/backup/tosnodb.bak.sh
#! /bin/sh
FILENAME=tosnodb`date +%Y%m%d%H%M`.gz
pg_dump tosnodb | gzip > /home/backup/tosno/$FILENAME
*********

************* /home/backup/fcmanagermedia.bak.sh
#! /bin/sh
FILENAME=fcmanagermedia`date +%Y%m%d%H%M`.tar.bz2
tar -jcvf /home/backup/$FILENAME /home/fcmanager/media
****************

*********** /home/jobs/type_active.sql
SELECT type_active(1);
*********


