Parse and push to db
====================

Automatisation
--------------

Add a cron job::

   PYTHONPATH=/home/pi/bdas

   # m h  dom mon dow   command
   @reboot /usr/bin/python3 /home/pi/bdas/bdas/RaspArDAS.py debug on calibration /home/pi/bdas/bdas/calibrations/cal_0002.dat > /home/pi/cronlog.log 2>&1

