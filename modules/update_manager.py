import os
import subprocess

from domain import clear

class Update_manager:

    def update(self) -> bool:
        APP_DIR = "/opt/rnd"

        clear()
        print("\n===================================")
        print("           RND UPDATER")
        print("===================================\n")

        if os.geteuid() != 0:
            print("[ERROR] Run RND as root.")
            return 

        if not os.path.isdir(f"{APP_DIR}/.git"):
            print("[ERROR] Git repository not found.")
            return 

        try:
            print("[INFO] Updating RND from GitHub...\n")

            subprocess.run(
                ["git", "-C", APP_DIR, "pull", "--ff-only"],
                check=True
            )

            requirements = f"{APP_DIR}/requirements.txt"
            pip = f"{APP_DIR}/.venv/bin/pip"

            if os.path.isfile(requirements):
                print("\n[INFO] Updating Python dependencies...\n")

                subprocess.run(
                    [pip, "install", "-r", requirements],
                    check=True
                )

            print("\n[SUCCESS] RND successfully updated!")
            print("[INFO] Restart RND to apply changes.\n")

            return 

        except subprocess.CalledProcessError as e:
            print(f"\n[ERROR] Update failed. Exit code: {e.returncode}")
            return 

        except Exception as e:
            print(f"\n[ERROR] Unexpected error: {e}")
            return 