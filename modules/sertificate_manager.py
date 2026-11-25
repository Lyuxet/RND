import subprocess
import os
from pathlib import Path

from domain import clear

class SertificateManager:
    def install(self):
        clear()
        print("\n===================================")
        print("       SOCAT ISTALLER")
        print("===================================\n")

        if os.geteuid() != 0:
            print("[ERROR] Run application as root.")
            return False

        if not self.run_command(["apt-get", "install", "cron", "socat"]):
            print("\n[ERROR] Не удалось установить CRON и SOCAT\n")
            return False

        if not self.install_acme("temp_mail@mail.ru"):
            return False

        return True

    def get_acme_path(self):
        import shutil
        paths = [
            shutil.which("acme.sh"),
            "/root/.acme.sh/acme.sh",
            "/home/acme/.acme.sh/acme.sh",
        ]

        for path in paths:
            if path and os.path.isfile(path):
                return path

        return None

        
    def run_command(self, command):
        try:
            subprocess.run(
                command,
                check=True
            )
            return True

        except subprocess.CalledProcessError:
            return False

    def install_acme(self, email: str):

        command = (
            f"curl -fsSL https://get.acme.sh | "
            f"sh -s email={email}"
        )   
        try:
            subprocess.run(
                command,
                shell=True,
                executable="/bin/bash",
                check=True
            )   
            print("[SUCCESS] ACME installed!")
            return True 
        except subprocess.CalledProcessError:
            print("[ERROR] ACME installation failed.")
            return False

    def issue_certificate(self, domain: str) -> bool:
        clear()
        print("\n===================================")
        print("       ISSUE CERTIFICATE")
        print("===================================\n")

        cert_dir = Path("/etc/nginx/sites-available")
        cert_dir.mkdir(parents=True, exist_ok=True)

        acme_path = self.get_acme_path()

        if not acme_path:
            print("[ERROR] acme.sh not found")
            return False

        path_key = "/opt/rem/privkey.key"
        path_fullchain = "/opt/rem/fullchain.pem"

        command = [
            acme_path,
            "--issue",
            "--standalone",
            "-d", domain,
            "--key-file", path_key,
            "--fullchain-file", path_fullchain,
            "--alpn",
            "--tlsport", "8443",
            "--force"
        ]

        try:
            result = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True
            )

            print(result.stdout)
            print(f"[SUCCESS] Certificate issued for {domain}")
            return True

        except subprocess.CalledProcessError as e:
            print("[ERROR] Certificate issuance failed")
            print(e.stderr)
            return False

        except FileNotFoundError:
            print("[ERROR] acme.sh not found")
            return False