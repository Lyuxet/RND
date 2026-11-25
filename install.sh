#!/bin/bash

set -e

APP_DIR="/opt/rnd"
REPO="https://github.com/Lyuxet/RND.git"
MAIN_FILE="main.py"

echo "==================================="
echo "           RND INSTALLER"
echo "==================================="

# Проверка root
if [ "$EUID" -ne 0 ]; then
    echo "[ERROR] Run installer as root."
    exit 1
fi

# Установка системных зависимостей
echo "[INFO] Installing dependencies..."

apt update
apt install -y python3 python3-venv python3-pip git

# Клонирование или обновление проекта
if [ ! -d "$APP_DIR/.git" ]; then
    echo "[INFO] Downloading RND..."
    git clone --depth 1 "$REPO" "$APP_DIR"
else
    echo "[INFO] Updating RND..."
    git -C "$APP_DIR" pull --ff-only
fi

cd "$APP_DIR"

# Проверка main.py
if [ ! -f "$MAIN_FILE" ]; then
    echo "[ERROR] main.py not found."
    exit 1
fi

# Создание виртуального окружения
echo "[INFO] Creating virtual environment..."

python3 -m venv "$APP_DIR/.venv"

# Установка Python зависимостей
echo "[INFO] Installing Python packages..."

if [ -f requirements.txt ]; then
    "$APP_DIR/.venv/bin/pip" install --upgrade pip
    "$APP_DIR/.venv/bin/pip" install -r requirements.txt
fi

# Создание команды rnd
echo "[INFO] Creating rnd command..."

cat > /usr/local/bin/rnd <<EOF
#!/bin/bash
cd "$APP_DIR"
exec "$APP_DIR/.venv/bin/python" "$APP_DIR/$MAIN_FILE" "\$@"
EOF

chmod +x /usr/local/bin/rnd

# Проверка
if [ ! -x /usr/local/bin/rnd ]; then
    echo "[ERROR] Failed to create rnd command."
    exit 1
fi

echo
echo "==================================="
echo "       RND INSTALLED SUCCESSFULLY"
echo "==================================="
echo
echo "Install to /opt/rnd"
echo "Create .env"
echo "Run: rnd"
echo "Update: bash install.sh"
echo