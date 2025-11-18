#!/usr/bin/env python3

import sys
import json
import subprocess
import re
import os

# --- Configuração dos Links ---
LINKS = [
    {
        "nome": "DigitalNet",
        "iface": "ppp1"
    },
    {
        "nome": "Vivo",
        "iface": "ppp0"
    }
    # Adicione mais links aqui
]

# --- IPs para Teste ---
# O script considera o link "UP" se *qualquer um* destes IPs responder.
IPS_TESTE = [
    '8.8.8.8',
    '8.8.4.4',
    '200.160.0.8',
    '177.74.129.201',
    '31.13.80.8'
]

# --- Configurações de Ping ---
# Quantos pings enviar para CADA IP
NUMERO_DE_PINGS = 3
# Timeout (em segundos) para o comando 'ping'.
TIMEOUT_POR_HOST_SEC = 2


def perform_discovery():
    """
    Gera um JSON LLD para o Zabbix, descobrindo APENAS os links.
    """
    discovery_data = []

    for link in LINKS:
        item = {
            "{#LINKNAME}": link["nome"],
            "{#INTERFACE}": link["iface"]
        }
        discovery_data.append(item)

    print(json.dumps({"data": discovery_data}, indent=2))

def check_link_status(interface):
    """
    Verifica o status de um link (interface).
    Testa todos os IPs em IPS_TESTE.
    Retorna "1" (UP) se *qualquer* IP responder.
    Retorna "0" (DOWN) se *todos* os IPs falharem.
    """

    if not re.match(r'^[a-zA-Z0-9.-]+$', interface):
        return "0"

    for host in IPS_TESTE:
        if not host:
            continue

        cmd = ['ping', '-I', interface,
               '-c', str(NUMERO_DE_PINGS),
               '-W', str(TIMEOUT_POR_HOST_SEC),
               host]

        try:
            timeout_total = (TIMEOUT_POR_HOST_SEC * NUMERO_DE_PINGS) + 2

            result = subprocess.run(cmd,
                                    capture_output=True,
                                    text=True,
                                    check=False,
                                    timeout=timeout_total)

            if result.returncode == 0:
                return "1"

        except subprocess.TimeoutExpired:
            pass
        except Exception as e:
            pass

    return "0"

def main():
    """
    Função principal.
    """
    if len(sys.argv) < 2:
        print(f"Uso: {sys.argv[0]} [--discover | --check <interface>]", file=sys.stderr)
        sys.exit(1)

    modo = sys.argv[1]

    if modo == '--discover':
        perform_discovery()

    elif modo == '--check':
        if len(sys.argv) != 3:
            print(f"Uso: {sys.argv[0]} --check <interface>", file=sys.stderr)
            sys.exit(1)

        interface = sys.argv[2]
        print(check_link_status(interface))

    else:
        print(f"Modo desconhecido: {modo}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
