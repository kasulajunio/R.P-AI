# Arquitetura

engine.py preserva o ponto de entrada do esqueleto de Fabio. official_core/engine.py contem MasterEngine, controle de caminhos, preparacao dos cinco modulos, diagnostico e operacoes SQLite/SHA-256. official_core/cli.py centraliza argumentos, JSON e menu. O nucleo e standard-library only.

## Invariantes

- Construir MasterEngine nao escreve nada.
- setup_structure cria somente a raiz escolhida e seus arquivos internos.
- Arquivos existentes nao sao substituidos pelo gerador.
- Links simbolicos e junctions detectaveis nos caminhos de workspace sao recusados.
- Caminhos relativos nao aceitam travessia, nomes reservados ou separadores ambiguos.
- Banco usa parametros, nunca interpolacao SQL de notas.
- Notas nao sao secretas e sao limitadas em tamanho; listagem tem limite de 100.
- Hash le arquivos regulares com limite de 1 GiB e streaming.
- A unica execucao externa do diagnostico e nvidia-smi por lista de argumentos, sem shell e com timeout.
- Venv so e criado por opcao explicita. Seu executavel Python pode ser um symlink normal gerado pelo proprio venv.

## Limites de seguranca

As verificacoes de caminho nao eliminam todas as condicoes de corrida de um sistema de arquivos controlado por um atacante. Nao use workspace gravavel por usuarios nao confiaveis. Hardlinks, drivers maliciosos e interpretadores comprometidos nao sao isolados pelo motor. Em POSIX, criacao tenta restringir permissoes; isso nao substitui revisao de ACLs no Windows.

## Como adicionar modulo

Crie API explicita, valide entradas, documente side effects, acrescente testes offline e revise licencas. Separar prepare de download, install, run e destroy. Nenhuma extensao pode abrir rede ou instalar dependencias durante init. Trate configuracoes do workspace como dados nao confiaveis. Nao use eval, exec de entrada ou shell=True.
