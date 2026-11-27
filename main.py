import sys

from system import get_system_info
from modules.installer import NodeInstaller
from domain import clear
from modules.update_manager import Update_manager





def print_header():

    info = get_system_info()

    clear()

    print("=" * 50)
    print("       RND - REMNAWAVE NODE DEPLOYER")
    print("=" * 50)

    print("\n SERVER INFORMATION\n")

    print(f" OS:           {info['os']} {info['version']}")
    print(f" IP:           {info['ip']}")
    print(f" HOSTNAME:     {info['hostname']}")
    print(f" CPU:          {info['cpu']} cores")
    print(f" RAM:          {info['ram']}")

    status = "ROOT" if info["root"] else "NOT ROOT"

    print(f" PRIVILEGES:   {status}")

    print("\n" + "=" * 50)


def main_menu():

    while True:

        print_header()

        print("\n MAIN MENU\n")

        print(" [1] Install Remnawave Node")
        print(" [2] Configure protocols")
        print(" [3] Configure Nginx")
        print(" [4] Configure Docker")
        print(" [5] Update components")
        print(" [6] Uninstall")

        print("\n [0] Exit")

        print("\n" + "=" * 50)

        choice = input("\n Select option: ").strip()

        if choice == "1":
            installer = NodeInstaller()
            installer.run()

        elif choice == "2":
            print("\n Protocol configuration is not implemented yet.")

        elif choice == "3":
            print("\n Nginx configuration is not implemented yet.")

        elif choice == "4":
            print("\n Configure Docker is not implemented yet.")

        elif choice == "5":
            updater = Update_manager()
            updater.update()

        elif choice == "6":
            print("\n Uninstaller is not implemented yet.")

        elif choice == "0":
            print("\n Goodbye!")
            sys.exit(0)

        else:
            print("\n Invalid option.")

        input("\n Press Enter to continue...")


if __name__ == "__main__":

    if not get_system_info()["root"]:
        print("Please run RND as root.")
        sys.exit(1)

    main_menu()