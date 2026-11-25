import os
import shutil
import socket
import re

from system import get_system_info
from domain import clear
from modules.docker_manager import DockerManager
from modules.nginx_manger import NginxManager
from modules.remnawave_manager import RemnawaveManager
from modules.sertificate_manager import SertificateManager


class NodeInstaller:

    def __init__(self):
        self.config = {}

    def check_system(self):

        clear()

        print("\n[ SYSTEM CHECK ]\n")

        info = get_system_info()

        if not info["root"]:
            print("[ERROR] Root privileges required.")
            return False

        print("[OK] Root privileges")

        if info["os"] not in ["ubuntu", "debian"]:
            print("[ERROR] Unsupported operating system.")
            return False

        print(f"[OK] OS: {info['os']} {info['version']}")

        if shutil.disk_usage("/").free < 2 * 1024**3:
            print("[WARNING] Less than 2 GB free disk space.")
        else:
            print("[OK] Disk space")

        if shutil.which("docker"):
            print("[OK] Docker установлен")
        else:
            print("[INFO] Docker не установлен")

        if shutil.which("nginx"):
            print("[OK] Nginx установлен")
        else:
            print("[INFO] Nginx не установлен")

        return True

    def get_configuration(self):

        print("\n[ КОНФИГУРАЦИЯ НОДЫ ]\n")
        print("\nВыйти в меню Ctrl+C")

        try:

            while True:
                ip = input("IP сервера: ").strip()

                try:
                    socket.inet_pton(socket.AF_INET, ip)
                    break
                except OSError:
                    print("[ERROR] Ошибка ввода IPV4.")


            while True:
                domain = input("Домен ноды: ").strip().lower()

                if re.fullmatch(
                    r"(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,}",
                    domain
                ):
                    break

                print("[ERROR] Ошибка ввода домена.")

            while True:
                port = input("Node порт [443]: ").strip() or "443"

                if port.isdigit() and 1 <= int(port) <= 65535:
                    break

                print("[ERROR] Ошибка ввода порта.")

            print("\n[ ВЫБЕРЕТЕ ПРОТОКОЛ ]\n")

            print("[1] VLESS TCP")
            print("[2] Hysteria")
            print("[3] Both")

            while True:
                protocol = input("\nSelect protocol: ").strip()

                if protocol in ["1", "2", "3"]:
                    break

                print("[ERROR] Ошибка ввода.")

            protocols = {
                "1": ["vless_tcp"],
                "2": ["hysteria"],
                "3": ["vless_tcp", "hysteria"]
            }

            self.config = {
                "ip": ip,
                "domain": domain,
                "port": int(port),
                "protocols": protocols[protocol]
            }
        except KeyboardInterrupt:
            raise

    def show_configuration(self):

        clear()

        print("\n" + "=" * 45)
        print("       КОНФИГУРАЦИЯ УСТАНОВКИ")
        print("=" * 45)

        print(f"Server IP:  {self.config['ip']}")
        print(f"Domain:     {self.config['domain']}")
        print(f"Port:       {self.config['port']}")

        print("Protocols:")

        for protocol in self.config["protocols"]:
            print(f"  - {protocol}")

        print("=" * 45)

        confirm = input("\Продолжить? [y/N]: ").strip().lower()

        return confirm == "y"

    def run(self):

        print("\nСтарт установщика Remnawave Node...")

        if not self.check_system():
            return

        try:
            self.get_configuration()

        except KeyboardInterrupt:
            return

        if not self.show_configuration():
            print("\nInstallation cancelled.")
            return

        print("\n[OK] Кофнигурация принята.")

        if not self.install_docker():
            print("\n[ERROR] Не возможно продолжить без DOCKER\n")
            return

        if not self.install_sertificate():
            print("\n[ERROR] Не возможно продолжить без CRON, SOCAT and ACME\n")
            return

        if not self.issue_sertificate():
            print(f"\n[ERROR] Не возможно продолжить без выпуска сертификатов\n")
            return
 
        
        if not self.install_nginx():
            print("\n[ERROR] Невозможно продолжить без NGINX\n")
            return

        if not self.create_nginx_file():
            print("\n[ERROR] Не возможно продолжить без конфигурационного файла NGINX\n")
            return


        if not self.create_node():
            print("\n[ERROR] Не возможно продолжить без ноды в Remnawave\n")
            return

        secret_key = self.get_secret_key_node()

        if not secret_key:
            print("\n[ERROR] Не возможно продолжить без ключа ноды Remnawave\n")
            return
        

        if not self.docker_up_node(secret_key=secret_key):
            print("\n[ERROR] Не возможно продолжить без ноды в Docker\n")
            return

        
        print("\n[SUCCESS] Сервер готов к работе\n")
        return


    def create_nginx_file(self):
        nginx = NginxManager()
        domain = self.config["doamin"]

        if nginx.create_nginx_file(domain=domain):
            print("\n[OK] Конфигурационный файл NGINX успешно создан\n")
            return True

        print("\n[ERROR] Ошибка создания конфигурационного файла NGINX\ns")
        return False

        
    

    def issue_sertificate(self):
        sertificate = SertificateManager()
        domain = self.config["domain"]

        if sertificate.issue_certificate(domain=domain):
            print(f"\n[OK] Сертификаты для домена {domain} успешно выпущены")
            return True

        print(f"\n[ERROR] Не удалось выпустить сертификаты для домена {domain}\n")
        return False

    

    def install_docker(self):

        docker = DockerManager()

        if docker.install():
            print("\n[OK] Docker УСПЕШНО УСТАНОВЛЕН.")
            return True

        print("\n[ERROR] Произошла ошибка во время установки Docker\n")
        return False

    

    def install_sertificate(self):
        sertificate = SertificateManager()

        if sertificate.install():
            print("\n[OK] CRON, SOCAT and ACME УСПЕШНО УСТАНОВЛЕНЫ")
            return True

        print("\n[ERROR] Произошла ошбика во время установки CRON, SOCAT and ACME\n")
        return False


    

    def install_nginx(self):
        nginx = NginxManager()

        if nginx.install():
            print("\n[OK] Nginx УСПЕШНО УСТАНОВЛЕН\n")
            return True

        print("\n[ERROR] Произошла ошибка во время установки Nginx\n")
        return False


    def create_node(self):
        remnawave = RemnawaveManager()

        ip = self.config["ip"];
        domain = self.config["domain"]
        port = self.config["port"]

        if remnawave.node_create(ip=ip, domain=domain, port=port):
            print("\n[OK] Нода успешно созадана в remnawave\n")
            return True

        print("\n[ERROR] Не удалось создать ноду в remnawave\n")
        return False

    def get_secret_key_node(self):
        remnawave = RemnawaveManager()

        secret_key = remnawave.get_secret_key_node()

        return secret_key

    def docker_up_node(self, secret_key):

        docker = DockerManager()

        if docker.node_up(secret_key=secret_key):
            print("\n[OK] Нода успешно поднята в Docker\n")
            return True

        return False
        

