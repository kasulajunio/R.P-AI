# Arquitetura

- engine.py: entrada compativel com o esqueleto original e menu.
- boot.py / official_core/bootstrap.py: boot offline nao interativo, deteccao de plataforma, criacao e verificacao de venv e chamada opcional da CLI.
- official_core/engine.py: MasterEngine, caminhos, estrutura, diagnostico, SQLite e SHA-256.
- official_core/services.py: notas CRUD/busca/exportacao, tarefas e backup/verificacao do banco.
- official_core/cli.py: argumentos, saida JSON e menu.
- scripts/check_secrets.py: triagem de blobs Git alcancaveis, sem exibir valores.

O nucleo usa somente biblioteca padrao. Construir MasterEngine nao grava arquivos. Init permanece offline e nao inicia venv. O boot cria venv por padrao porque essa e a acao explicita do comando boot; --without-venv desativa isso. Nenhum dos dois instala pacotes globais ou baixa modelos.

## Invariantes

Caminhos de workspace recusam travessia, nomes reservados e links/junctions detectaveis. Geradores, exportacoes e backups nao sobrescrevem arquivos existentes. Edicao de notas e mudanca de estado de tarefas sao operacoes explicitas no SQLite. Exclusao de notas exige --confirm. Banco usa parametros SQL. Conexoes sao fechadas. Listagens sao limitadas a 100 e exportacao JSON a 10000 notas.

Backup usa sqlite3.Connection.backup e quick_check, nao copia diretamente um banco ativo. Inclui as tabelas do banco, nao o workspace inteiro. Nao ha restauracao automatica. SHA-256 usa streaming e limite de 1 GiB; nao e criptografia.

O diagnostico executa nvidia-smi com timeout se estiver presente. O boot executa o Python do venv com argumentos fixos, sem shell, para conferir o ambiente. Nao executa scripts de modelos nem aceita entrada como codigo.

## Limites de seguranca

Venv nao e sandbox. Nao use workspace ou interpretador controlado por terceiros. Checagens nao eliminam corridas de filesystem, hardlinks ou comprometimento do sistema. Permissoes POSIX nao substituem ACLs no Windows. O executavel Python do venv pode ser um symlink normal criado pelo proprio Python.

Novos modulos devem separar prepare, download, install, run e destroy, documentar efeitos, revisar licencas e incluir testes. Nunca tratar preparar diretorios como recurso implementado.
