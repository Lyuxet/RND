import os
import subprocess
import re

from pathlib import Path
from domain import clear


class NginxManager:

    def __init__(self):
        self.path = Path("/etc/nginx/sites-available")
        self.template_path = Path("nginx_template.conf")
        self.zaglushka_path = Path("zaglushka")

    def create_nginx_file(self, domain: str):
        clear()
        print("\n===================================")
        print("            START NGINX")
        print("===================================\n")

        if os.geteuid() != 0:
            print("[ERROR] Run application as root.")
            return False

        if not self.template_path.exists():
            print("[ERROR] Nginx template not found.")
            return False

        config = self.template_path.read_text(encoding="utf-8")

        config, count = re.subn(
            r"(^\s*server_name\s+)\*;",
            rf"\g<1>{domain};",
            config,
            flags=re.MULTILINE
        )

        if count != 2:
            print(f"[ERROR] Expected 2 server_name directives, found {count}.")
            return False

        self.config = self.path / domain

        if self.config.exists():
            print("[ERROR] Config already exists.")
            return False

        self.config.write_text(config, encoding="utf-8")

        if not self.copy_zaglushka_to_var():
            return False

        if not self.enable_site():
            return False

        if not self.restart_nginx():
            return False

        print(f"[SUCCESS] START NGINX: {self.config}")

        return True


    def restart_nginx(self):
        if os.geteuid() != 0:
            print("[ERROR] Run application as root.")
            return False

        command = ["systemctl", "restart", "nginx"]

        if not self.run_command(command=command):
            print("[ERROR] Не удалось перезапустить службу Nginx")
            return False

        return True        


    def enable_site(self):
        if os.geteuid() != 0:
            print("[ERROR] Run application as root.")
            return False
        
        if not self.config.exists() or self.config == None:
            print("[ERROR] Config not found")
            return False

        command = ["ln", "-s", self.config, "/etc/nginx/sites-enabled/"]

        if not self.run_command(command=command):
            print(f"[ERROR] Не удалось создать символическую ссылку для {self.path}")
            return False

        print("[OK] Сайт успешно активирован")
        return True


    def copy_zaglushka_to_var(self):
        if os.geteuid() != 0:
            print("[ERROR] Run application as root.")
            return False
        
        if not self.zaglushka_path.exists():
            print("[ERROR] Nginx zaglushka not found.")
            return False

        purpose_path = Path("/var/www")

        if not purpose_path.exists():
            print("[ERROR] Не удалось скопировать заглушку, /var/www not found.")
            return False


        command = ["cp", "-r", self.zaglushka_path, "/var/www"]

        if not self.run_command(command=command):
            print("[ERROR] Не удалось скопировать зашлушку")
            return False

        print("[OK] Заглушка успешно скопирована")
        return True
        




    def run_command(self, command):
        try:
            subprocess.run(
                command,
                check=True
            )
            return True

        except subprocess.CalledProcessError:
            return False

    def check_nginx(self):

        try:
            nginx =  subprocess.run(["nginx", "-v"],
                capture_output=True,
                text=True)

            return {"nginx": nginx.returncode == 0}
        except FileNotFoundError:
                return {"nginx": False}
        

    def install(self):
        clear()
        print("\n===================================")
        print("       NGINX ISTALLER")
        print("===================================\n")

        if os.geteuid() != 0:
            print("[ERROR] Run application as root.")
            return False

        status = self.check_nginx()
        
        if status["nginx"]:
            return True
        
        if not self.run_command(["apt", "install", "nginx"]):
            return False

        if not self.run_command([
            "systemctl", "enable", "--now", "docker"
            ]):
            return False
        
        status = self.check_nginx()

        if status["nginx"]:
            print("\n===================================")
            print("[SUCCESS] Nginx installed!")
            print("===================================")
            return True
        
        print("[ERROR] Nginx verification failed.")
        return False
