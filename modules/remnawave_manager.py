import os
from dotenv import load_dotenv
import json

import requests

from domain import clear, get_ip_country, generate_7_digits

load_dotenv()

PANEL_URL = os.getenv("PANEL_URL").rstrip("/")
API_KEY = os.getenv("API_KEY")

NODE_PORT = int(os.getenv("NODE_PORT", "2222"))


class RemnawaveManager:
    def node_create(self, ip: str, domain: str, port: int):
        clear()

        print("\n===================================")
        print("       CREATE REMNAWAVE PROFILE")
        print("===================================\n")
        
            
        try:
            country = get_ip_country(ip=ip)
            code = generate_7_digits()

            data = self.update_progile_congig(ip=ip, domain=domain,port=port, 
                                              country=country, code=code)

            response = requests.post(f"{PANEL_URL}/api/config-profiles",
                    headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {API_KEY}"
                    },
                    json={
                    "name": f"{country}_{code}",
                    "config": data
                    }
                )

            profile_uuid = response.json()["response"]["uuid"]
            
            response = requests.get(
            f"{PANEL_URL}/api/config-profiles/{profile_uuid}/inbounds",
            headers={
            "Authorization": f"Bearer {API_KEY}"
            }
        )

            inbound_uuid = response.json()["response"]["inbounds"][0]["uuid"]


            print("CREATE Node...\n")


            response = requests.post(f"{PANEL_URL}/api/nodes",
                headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {API_KEY}"
                },
                json={
                "name": f"{country}_{code}",
                "address": ip,
                "port": NODE_PORT,
                "proxyUrl": None,
                "isTrafficTrackingActive": False,
                "trafficLimitBytes": 0,
                "notifyPercent": 0,
                "trafficResetDay": 1,
                "countryCode": "XX",
                "consumptionMultiplier": 0,
                "nodeConsumptionMultiplier": 0,
                "configProfile": {
                    "activeConfigProfileUuid": profile_uuid,
                    "activeInbounds": [
                    inbound_uuid
                    ]
                },
                "providerUuid": None,
                "tags": [],
                "activePluginUuid": None,
                "integrationUuids": [],
                "note": "",
                "ips": [
                    {
                    "ip": ip,
                    "status": "INBOUND"
                    }
                ]
                }
            )
            return True
        
        except requests.exceptions.Timeout:
            print("\n[ERROR] Сервер слишком долго отвечает\n")
            return False

        except requests.exceptions.ConnectionError:
            print("\n[ERROR] Ошибка соединения с сервером\n")
            return False

        except requests.exceptions.HTTPError as e:
            print(f"\n[ERROR] HTTP ошибка: {e}\n")
            return False

        except requests.exceptions.JSONDecodeError:
            print("\n[ERROR] Ошибка обработки JSON\n")
            return False

        except FileNotFoundError:
            print("\n[ERROR] Файл конфигурации не найден\n")
            return False

        except json.JSONDecodeError:
            print("\n[ERROR] Ошибка чтения JSON-файла\n")
            return False

        except KeyError as e:
            print(f"\n[ERROR] Отсутствует ключ: {e}\n")
            return False

        except IndexError:
            print("\n[ERROR] Список пуст, невозможно получить элемент\n")
            return False

        except Exception as e:
            print(f"\n[ERROR] Неизвестная ошибка: {type(e).__name__}: {e}\n")
            return False


    def update_progile_congig(self, ip: str, domain: str, port: int, country: str, code: int):
        try:
            with open("profile_config_template.json", "r", encoding="utf-8") as file:
                data = json.load(file)

                inbounds = data["inbounds"]

                for inbound in inbounds:
                    inbound["port"] = port
                    streamSettings = inbound["streamSettings"]
                    security = streamSettings["security"]

                    tag = f"{country}_{code}"

                    if security == "reality":
                        inbound["tag"] = f"VLESS_{tag}"
                        realitySettings = streamSettings["realitySettings"]
                        realitySettings["serverNames"][0] = domain

                    elif security == "tls":
                        inbound["tag"] = f"HYSTERIA_{tag}"

            return data     
        except:
            raise


    def get_secret_key_node(self):

        try:
            response = requests.get(
                f"{PANEL_URL}/api/keygen",
                headers={
                    "Authorization": f"Bearer {API_KEY}"
                },
                timeout=15
            )

            response.raise_for_status()

            secret_key = response.json()["response"]["secretKey"]

            return secret_key

        except requests.exceptions.Timeout:
            print("\n[ERROR] Сервер слишком долго отвечает\n")
            return False

        except requests.exceptions.ConnectionError:
            print("\n[ERROR] Ошибка соединения с сервером\n")
            return False

        except requests.exceptions.HTTPError as e:
            print(f"\n[ERROR] HTTP ошибка: {e}\n")
            return False

        except requests.exceptions.JSONDecodeError:
            print("\n[ERROR] Ошибка обработки JSON\n")
            return False

        except FileNotFoundError:
            print("\n[ERROR] Файл конфигурации не найден\n")
            return False

        except json.JSONDecodeError:
            print("\n[ERROR] Ошибка чтения JSON-файла\n")
            return False
        except Exception as e:
            print(f"\n[ERROR] Неизвестная ошибка: {type(e).__name__}: {e}\n")
            return False




                    



