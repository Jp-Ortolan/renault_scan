"""
Módulo para importação e formatação de datasets para detecção de defeitos.
Suporta múltiplos formatos e estruturas de dados.
"""

import os
import cv2
import numpy as np
from typing import List, Tuple, Optional, Dict
from pathlib import Path
import json


class ProcessadorDataset:
    """
    Classe para processar e preparar datasets de imagens.
    """
    
    def __init__(self, pasta_base: str = "imagens_para_analisar"):
        """
        Inicializa o processador de dataset.
        
        Args:
            pasta_base (str): Pasta base onde estão as imagens
        """
        self.pasta_base = pasta_base
        self.extensoes_validas = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
        
    def listar_imagens(self, pasta: Optional[str] = None) -> List[str]:
        """
        Lista todas as imagens em uma pasta.
        
        Args:
            pasta (str, opcional): Pasta para listar (usa pasta_base se None)
            
        Returns:
            List[str]: Lista de caminhos para imagens
        """
        if pasta is None:
            pasta = self.pasta_base
        
        imagens = []
        if not os.path.exists(pasta):
            return imagens
        
        for arquivo in os.listdir(pasta):
            if any(arquivo.lower().endswith(ext) for ext in self.extensoes_validas):
                caminho_completo = os.path.join(pasta, arquivo)
                imagens.append(caminho_completo)
        
        return sorted(imagens)
    
    def carregar_imagens(self, caminhos: Optional[List[str]] = None, 
                        redimensionar: Optional[Tuple[int, int]] = (224, 224)) -> List[np.ndarray]:
        """
        Carrega imagens de arquivos.
        
        Args:
            caminhos (List[str], opcional): Lista de caminhos (usa pasta_base se None)
            redimensionar (Tuple[int, int], opcional): Dimensões desejadas
            
        Returns:
            List[np.ndarray]: Lista de imagens carregadas
        """
        if caminhos is None:
            caminhos = self.listar_imagens()
        
        imagens = []
        for caminho in caminhos:
            try:
                img = cv2.imread(caminho)
                if img is None:
                    print(f"Aviso: Não foi possível carregar {caminho}")
                    continue
                
                if redimensionar:
                    img = cv2.resize(img, redimensionar)
                
                imagens.append(img)
            except Exception as e:
                print(f"Erro ao carregar {caminho}: {e}")
        
        return imagens
    
    def organizar_por_classes(self, estrutura_classes: Dict[str, str] = None) -> Dict[str, List[str]]:
        """
        Organiza imagens por classes baseado em padrões de nome ou estrutura de pastas.
        
        Args:
            estrutura_classes (Dict[str, str], opcional): Mapeamento de padrões para classes
                         exemplo: {"defeito": ["damage", "scratch"], "ok": ["normal", "intacto"]}
        
        Returns:
            Dict[str, List[str]]: Dicionário mapeando classes para listas de caminhos
        """
        if estrutura_classes is None:
            # Padrão simples baseado em palavras-chave no nome do arquivo
            estrutura_classes = {
                "defeito": ["damage", "scratch", "dent", "broken", "defeito", "batida", "colisao", "risco"],
                "ok": ["ok", "normal", "intact", "good", "fine", "bm", "bmw", "carro-completo", "carro-prateado"]
            }
        
        imagens = self.listar_imagens()
        imagens_por_classe = {classe: [] for classe in estrutura_classes.keys()}
        imagens_nao_classificadas = []
        
        for caminho in imagens:
            nome_arquivo = os.path.basename(caminho).lower()
            classificada = False
            
            for classe, palavras_chave in estrutura_classes.items():
                if any(palavra in nome_arquivo for palavra in palavras_chave):
                    imagens_por_classe[classe].append(caminho)
                    classificada = True
                    break
            
            if not classificada:
                imagens_nao_classificadas.append(caminho)
        
        if imagens_nao_classificadas:
            print(f"AVISO: {len(imagens_nao_classificadas)} imagens não classificadas:")
            for img in imagens_nao_classificadas[:5]:  # Mostra primeiras 5
                print(f"  - {os.path.basename(img)}")
            if len(imagens_nao_classificadas) > 5:
                print(f"  ... e mais {len(imagens_nao_classificadas) - 5} imagens")
        
        return imagens_por_classe
    
    def criar_dataset_estruturado(self, pasta_destino: str = "dataset_estruturado"):
        """
        Cria uma estrutura de dataset organizada por classes.
        
        Args:
            pasta_destino (str): Pasta onde criar a estrutura
        """
        print("Organizando dataset por classes...")
        imagens_por_classe = self.organizar_por_classes()
        
        # Cria estrutura de pastas
        for classe in imagens_por_classe.keys():
            pasta_classe = os.path.join(pasta_destino, classe)
            os.makedirs(pasta_classe, exist_ok=True)
        
        # Copia imagens (ou cria links simbólicos)
        total_copiadas = 0
        for classe, caminhos in imagens_por_classe.items():
            pasta_classe = os.path.join(pasta_destino, classe)
            for caminho in caminhos:
                nome_arquivo = os.path.basename(caminho)
                destino = os.path.join(pasta_classe, nome_arquivo)
                
                # Verifica se já existe
                if not os.path.exists(destino):
                    try:
                        # Copia o arquivo
                        import shutil
                        shutil.copy2(caminho, destino)
                        total_copiadas += 1
                    except Exception as e:
                        print(f"Erro ao copiar {caminho}: {e}")
        
        print(f"\nDataset estruturado criado em: {pasta_destino}")
        print(f"Total de imagens organizadas: {total_copiadas}")
        
        # Mostra estatísticas
        for classe, caminhos in imagens_por_classe.items():
            print(f"  {classe}: {len(caminhos)} imagens")
    
    def obter_estatisticas_dataset(self) -> Dict:
        """
        Obtém estatísticas sobre o dataset.
        
        Returns:
            Dict: Estatísticas do dataset
        """
        imagens = self.listar_imagens()
        imagens_por_classe = self.organizar_por_classes()
        
        # Carrega algumas imagens para obter dimensões
        dimensoes = []
        for caminho in imagens[:10]:  # Primeiras 10 para amostra
            img = cv2.imread(caminho)
            if img is not None:
                dimensoes.append(img.shape)
        
        # Calcula estatísticas de dimensões
        if dimensoes:
            alturas = [d[0] for d in dimensoes]
            larguras = [d[1] for d in dimensoes]
            canais = [d[2] if len(d) > 2 else 1 for d in dimensoes]
        else:
            alturas = larguras = canais = []
        
        estatisticas = {
            "total_imagens": len(imagens),
            "por_classe": {classe: len(caminhos) 
                          for classe, caminhos in imagens_por_classe.items()},
            "dimensoes_medias": {
                "altura": np.mean(alturas) if alturas else 0,
                "largura": np.mean(larguras) if larguras else 0,
                "canais": np.median(canais) if canais else 3
            },
            "formato_canais": "RGB" if (canais and np.median(canais) == 3) else "Grayscale"
        }
        
        return estatisticas
    
    def formatar_para_treinamento(self, tamanho_desejado: Tuple[int, int] = (224, 224),
                                  normalizar: bool = True) -> Dict:
        """
        Formata o dataset para uso em treinamento.
        
        Args:
            tamanho_desejado (Tuple[int, int]): Tamanho das imagens
            normalizar (bool): Se deve normalizar pixels [0, 255] -> [0, 1]
        
        Returns:
            Dict: Dados formatados
        """
        imagens_por_classe = self.organizar_por_classes()
        
        X = []  # Imagens
        y = []  # Labels
        mapeamento_classes = {classe: i for i, classe in enumerate(imagens_por_classe.keys())}
        
        for classe, caminhos in imagens_por_classe.items():
            for caminho in caminhos:
                img = cv2.imread(caminho)
                if img is None:
                    continue
                
                # Redimensiona
                img_resized = cv2.resize(img, tamanho_desejado)
                
                # Normaliza se necessário
                if normalizar:
                    img_resized = img_resized.astype(np.float32) / 255.0
                
                X.append(img_resized)
                y.append(mapeamento_classes[classe])
        
        return {
            "X": np.array(X),
            "y": np.array(y),
            "mapeamento_classes": {v: k for k, v in mapeamento_classes.items()},
            "num_classes": len(mapeamento_classes)
        }
    
    def exportar_metadados(self, caminho_saida: str = "metadados_dataset.json"):
        """
        Exporta metadados sobre o dataset.
        
        Args:
            caminho_saida (str): Caminho para salvar o arquivo JSON
        """
        estatisticas = self.obter_estatisticas_dataset()
        
        with open(caminho_saida, 'w', encoding='utf-8') as f:
            json.dump(estatisticas, f, indent=2, ensure_ascii=False)
        
        print(f"Metadados exportados para: {caminho_saida}")
        return estatisticas


def carregar_dataset_kaggle_format(pasta_dataset: str) -> Dict:
    """
    Carrega dataset no formato Kaggle (pastas por classe).
    
    Args:
        pasta_dataset (str): Pasta do dataset
        
    Returns:
        Dict: Dados do dataset
    """
    processador = ProcessadorDataset(pasta_dataset)
    return processador.formatar_para_treinamento()


if __name__ == "__main__":
    # Teste do processador de dataset
    print("Processador de Dataset para Detecção de Defeitos")
    print("=" * 60)
    
    processador = ProcessadorDataset("imagens_para_analisar")
    
    # Mostra estatísticas
    print("\nEstatísticas do Dataset:")
    estatisticas = processador.obter_estatisticas_dataset()
    print(f"Total de imagens: {estatisticas['total_imagens']}")
    print(f"Por classe: {estatisticas['por_classe']}")
    
    # Exporta metadados
    processador.exportar_metadados()
    
    print("\nProcessador inicializado com sucesso!")

