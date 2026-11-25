import os
import subprocess
import re

from pathlib import Path
from domain import clear


class NginxManager:

    def __init__(self):
        self.path = Path("/etc/nginx/etc/nginx/sites-available")
        self.template_path = Path(__file__).parent / "nginx_template.conf"

    def create_nginx_file(self, domain: str):
        clear()
        print("\n===================================")
        print("       CREATE NGINX FILE")
        print("===================================\n")

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

        print(f"[SUCCESS] Config created: {self.config}")

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
        
        if not self.run_command(["apt", "install", "nginx", "-Y"]):
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
