"""
Script para testar importações e verificar se todos os módulos estão funcionando.
"""

import sys
import os

# Adiciona src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

print("=" * 60)
print("TESTE DE IMPORTACOES - Projeto Deteccao de Defeitos")
print("=" * 60)

# Teste 1: Algoritmos basicos
print("\n[1] Testando Algoritmo Aleatorio...")
try:
    from algoritmos_deteccao import AlgoritmoAleatorio
    algo_aleat = AlgoritmoAleatorio(seed=42)
    print("   [OK] Algoritmo Aleatorio importado com sucesso!")
except Exception as e:
    print(f"   [ERRO] Erro: {e}")

print("\n[2] Testando Algoritmo Heuristico...")
try:
    from algoritmos_deteccao import AlgoritmoHeuristico
    algo_heur = AlgoritmoHeuristico()
    print("   [OK] Algoritmo Heuristico importado com sucesso!")
except Exception as e:
    print(f"   [ERRO] Erro: {e}")

# Teste 2: Deep Learning
print("\n[3] Testando Deep Learning...")
try:
    from deep_learning import AlgoritmoDeepLearning
    algo_dl = AlgoritmoDeepLearning()
    print("   [OK] Algoritmo Deep Learning importado com sucesso!")
except ImportError:
    print("   [AVISO] PyTorch nao instalado. Instale com: pip install torch torchvision")
except Exception as e:
    print(f"   [AVISO] Erro ao carregar Deep Learning: {e}")

# Teste 3: Preprocessamento
print("\n[4] Testando Preprocessamento de Dataset...")
try:
    from preprocessamento_dataset import ProcessadorDataset
    processador = ProcessadorDataset()
    print("   [OK] Processador de Dataset importado com sucesso!")
except Exception as e:
    print(f"   [ERRO] Erro: {e}")

# Teste 4: Sistema principal
print("\n[5] Testando Sistema Principal...")
try:
    from detectacao_defeitos import SistemaDetecaoDefeitos
    print("   [OK] Sistema Principal importado com sucesso!")
except Exception as e:
    print(f"   [ERRO] Erro: {e}")

print("\n" + "=" * 60)
print("TESTE COMPLETO!")
print("=" * 60)
print("\nSe todos os modulos foram importados com sucesso, voce pode executar:")
print("  python detectacao_defeitos.py")
print("\nPara instalar dependencias faltantes:")
print("  pip install -r requirements.txt")

