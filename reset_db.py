"""Script para resetar o banco de dados completamente"""
import os
import sys

# Adiciona o diretório do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import reset_database

if __name__ == '__main__':
    print("⚠️  ATENÇÃO: Esta operação vai APAGAR TODOS OS DADOS do banco de dados!")
    resposta = input("Tem certeza que deseja continuar? (digite 'SIM' para confirmar): ")
    
    if resposta == 'SIM':
        try:
            print("🔄 Resetando banco de dados...")
            reset_database()
            print("✅ Banco de dados resetado com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao resetar banco de dados: {e}")
            sys.exit(1)
    else:
        print("❌ Operação cancelada.")

