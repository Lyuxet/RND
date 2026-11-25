import os
import subprocess
from pathlib import Path
import yaml

from domain import clear


class DockerManager:

    def run_command(self, command):
        try:
            subprocess.run(
                command,
                check=True
            )
            return True

        except subprocess.CalledProcessError:
            return False

    def get_os_info(self):
        info = {}

        try:
            with open("/etc/os-release") as file:
                for line in file:
                    if "=" in line:
                        key, value = line.strip().split("=", 1)
                        info[key] = value.strip('"')

        except OSError:
            return None

        return info

    def check_docker(self):

        try:
            docker = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True
            )

            compose = subprocess.run(
                ["docker", "compose", "version"],
                capture_output=True,
                text=True
            )

            return {
                "docker": docker.returncode == 0,
                "compose": compose.returncode == 0
            }

        except FileNotFoundError:
            return {
                "docker": False,
                "compose": False
            }

    def install(self):
        clear()
        print("\n===================================")
        print("       DOCKER INSTALLER")
        print("===================================\n")
    
        if os.geteuid() != 0:
            print("[ERROR] Run application as root.")
            return False

        status = self.check_docker()

        if status["docker"] and status["compose"]:
            return True
        
        subprocess.run(
            "curl -fsSL https://get.docker.com | sh",
            shell=True,
            check=True
        )

        print("\n Starting Docker...")

        if not self.run_command([
            "systemctl", "enable", "--now", "docker"
        ]):
            return False

        status = self.check_docker()

        if status["docker"] and status["compose"]:
            print("\n===================================")
            print("[SUCCESS] Docker installed!")
            print("===================================")
            return True

        print("[ERROR] Docker verification failed.")
        return False


    def node_up(self, secret_key: str):
        clear()
        print("\n===================================")
        print("  DOCKER COMPOSE UP REMNAWAVE NODE")
        print("===================================\n")

        if os.geteuid() != 0:
            print("[ERROR] Run application as root.")
            return False

        try:
            data = self.update_docker_compose(secret_key=secret_key)

            base_dir = Path("/opt")
            project_dir = base_dir / "rem"

            project_dir.mkdir(parents=True, exist_ok=True)

            compose_file = project_dir / "docker-compose.yml"

            compose_file.write_text(
                yaml.safe_dump(
                        data,
                        allow_unicode=True,
                        sort_keys=False
                    ),
                    encoding="utf-8"
                )

            print(f"Папка создана: {project_dir}")
            print("docker-compose.yml создан")

            subprocess.run(
                ["docker", "compose", "up", "-d"],
                cwd=project_dir,
                check=True
            )

            try:
                subprocess.run(
                    ["docker", "compose", "logs", "-f"],
                    cwd=project_dir
                )
            except KeyboardInterrupt:
                print("Просмотр логов остановлен")

            return True

        except FileNotFoundError:
            print("\n[ERROR] Файл конфигурации не найден\n")
            return False
        
            


    def update_docker_compose(self, secret_key: str):

        try:
            with open("docker-compose_template.yml", "r", encoding="utf-8") as file:
                data = yaml.safe_load(file)

            environment = data["services"]["remnanode"]["environment"]

            for i, item in enumerate(environment):
                if item.startswith("SECRET_KEY="):
                    environment[i] = f"SECRET_KEY={secret_key}"
                    break
            else:
                environment.append(f"SECRET_KEY={secret_key}")

            return data

        except:
            raise

