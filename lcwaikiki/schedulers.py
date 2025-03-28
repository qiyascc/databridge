# scraper_apps/lcwaikiki/schedulers.py

import logging
import threading
import time
import atexit
import sys
from django.core.management import call_command
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)

class TaskScheduler:
    """
    Genel zamanlayıcı sınıfı - belirli aralıklarla Django komutlarını çalıştırır
    """
    def __init__(self):
        self._schedulers = []
        self._running = False
        self._main_thread = None
        
    def add_task(self, command_name, interval_hours, initial_delay_minutes=0):
        """
        Yeni bir periyodik görev ekler
        
        Args:
            command_name: Çalıştırılacak Django yönetim komutu adı
            interval_hours: Tekrar aralığı (saat)
            initial_delay_minutes: İlk çalıştırma için gecikme (dakika)
        """
        task = {
            'command': command_name,
            'interval': interval_hours * 3600,  # saat -> saniye
            'last_run': None,
            'next_run': timezone.now() + timedelta(minutes=initial_delay_minutes),
            'running': False
        }
        self._schedulers.append(task)
        logger.info(f"Task scheduled: {command_name} - every {interval_hours} hours "
                    f"(first run in {initial_delay_minutes} minutes)")
        
    def start(self):
        """Tüm zamanlanmış görevlerin izlenmesini başlatır"""
        if self._running:
            return
            
        self._running = True
        self._main_thread = threading.Thread(target=self._monitor, daemon=True)
        self._main_thread.start()
        
        # Uygulama kapanırken düzgün temizlik
        atexit.register(self.stop)
        
        logger.info("Task scheduler started")
        
    def stop(self):
        """Zamanlayıcıyı durdurur"""
        if not self._running:
            return
            
        self._running = False
        if self._main_thread and self._main_thread.is_alive():
            self._main_thread.join(timeout=5)
        logger.info("Task scheduler stopped")
        
    def _monitor(self):
        """Ana izleme döngüsü - uygun komutları zamanı geldiğinde çalıştırır"""
        while self._running and not sys.is_finalizing():
            now = timezone.now()
            
            for task in self._schedulers:
                if not task['running'] and now >= task['next_run']:
                    self._execute_task(task)
                    
            time.sleep(60)  # Her dakika kontrol et
    
    def _execute_task(self, task):
        """Belirli bir görevi çalıştırır"""
        task['running'] = True
        thread = threading.Thread(
            target=self._run_command,
            args=(task,),
            daemon=True
        )
        thread.start()
        
    def _run_command(self, task):
        """Django komutunu çalıştırıp görev durumunu günceller"""
        try:
            logger.info(f"Executing task: {task['command']}")
            call_command(task['command'])
            logger.info(f"Task completed: {task['command']}")
        except Exception as e:
            logger.error(f"Task error ({task['command']}): {str(e)}", exc_info=True)
        finally:
            # Görev durumunu güncelle
            task['running'] = False
            task['last_run'] = timezone.now()
            task['next_run'] = task['last_run'] + timedelta(seconds=task['interval'])
            logger.info(f"Next run for {task['command']}: {task['next_run']}")