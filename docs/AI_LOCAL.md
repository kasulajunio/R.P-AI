# IA local: preparacao sem promessas falsas

## Implementado

prepare ai cria a estrutura e um teste Python. prepare ai --venv cria um ambiente com venv e pip embarcado pelo Python, sem atualizar pacotes pela internet. Nenhum modelo e baixado e nenhuma inferencia e executada. O teste informa a ausencia de PyTorch sem tentar instalar nada.

## Por que o esqueleto original foi corrigido

- A expressao input(...) | input(...) nao e uma entrada valida; agora ha uma leitura por escolha.
- Nao usamos shell=True, pipeline lspci/grep nem wmic.
- nvidia-smi e apenas um indicador com timeout; nao prova que CUDA funciona.
- https://pytorch.org nao deve ser usado como indice pip generico. Uma instalacao futura deve usar o seletor oficial e o indice recomendado para a plataforma, nao uma URL improvisada.
- Nao atualizamos pip, instalamos varias bibliotecas pesadas ou baixamos modelos de forma silenciosa.
- Nao afirmamos que venv isola o sistema de codigo malicioso.

## Para ampliar depois

1. Registrar sistema, arquitetura, Python, memoria, armazenamento e autorizacao para downloads.
2. Consultar https://pytorch.org/get-started/locally/ e selecionar a plataforma real.
3. Fixar versoes e hashes em arquivo revisado, incluindo dependencias transitivas.
4. Separar CPU, CUDA e Android; nao escolher CUDA somente pelo nome da GPU.
5. Revisar licenca e origem de cada modelo; desabilitar execucao de codigo remoto por padrao.
6. Mostrar tamanho, destino e custo dos downloads antes da confirmacao.
7. Fazer smoke test pequeno, confirmar offline e medir uso de recursos.

A quantidade necessaria de RAM, VRAM e disco depende do modelo, quantizacao e backend. Nao ha garantia universal para celulares. Esta etapa futura ainda nao esta implementada.
