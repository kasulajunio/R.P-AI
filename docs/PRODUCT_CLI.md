# CLI R.P AI 0.2.0

Esta CLI e Python para funcionar tambem no Windows. Nao executa apt-get, pkg, sudo, shell=True, main.py inexistente nem requirements.txt ficticio. Preparacao e execucao conferem os retornos, e falha nao vira mensagem de sucesso.

## Uso sem instalacao de pacote

Na pasta clonada, com Python 3.10+:

```sh
python rpa.py install
python rpa.py run note-add "Plano" --body "Texto"
python rpa.py run note-list
python rpa.py status
python rpa.py update
```

Windows: py -3. Linux/macOS: python3 se necessario. Termux: python. O workspace padrao e .core na pasta atual, nao ~/.rpa. Para escolher outro local: python rpa.py --root CAMINHO install. Use sempre a mesma raiz. A raiz vem antes do comando, nao dentro de run.

## Registrar o comando literal rpa

Opcional, num ambiente virtual proprio com pip e setuptools>=68 ja instalados, dentro do clone:

```sh
python -m pip install --no-build-isolation --no-deps -e .
rpa install
rpa run note-list
rpa status
```

Nao use sudo nem instale no Python do sistema. O venv criado pelo boot deliberadamente nao inclui pip: ele serve para preparacao offline. Se quiser empacotar, prepare separadamente um venv com pip conforme a documentacao oficial do seu Python. Com --no-build-isolation, as ferramentas de build precisam existir; se faltarem, use python rpa.py diretamente. Um pip install comum pode acessar a rede para obter ferramentas de build. Nao ha publicacao no PyPI anunciada.

## Install

Cria estrutura e banco SQLite preservando arquivos existentes. Por padrao cria venv sem pip e sem downloads, com copia do Python, e executa esse interpretador em modo isolado para verificar versao e prefixo. Reutiliza o ambiente correto. --no-venv prepara ferramentas sem ML quando venv nao estiver disponivel. Python precisa existir antes de qualquer script Python.

## Run

Executa comandos implementados da CLI local. Sem argumentos, executa doctor.

```sh
python rpa.py run task-add "Revisar"
python rpa.py run task-list
python rpa.py run note-get 1
python rpa.py run db-backup backup-01.sqlite3
```

Use os IDs reais retornados no seu workspace. run nao e inferencia com modelo e nao inicia servico permanente.

## Update

Somente checkout limpo na branch main e origin oficial. Usa Git pull --ff-only, verifica retorno e aplica timeout. Recusa ZIP, instalacao em wheel, alteracoes locais e branch de desenvolvimento. Nao executa reset --hard, nao reinstala dependencias e nao modifica o sistema.

Esse comando acessa a rede apenas quando solicitado. Requer Git e autenticacao enquanto o repositorio for privado. Confirme os testes da versao nova antes de confiar nela. Nao ha atualizacao automatica por padrao.

## Status

Mostra versao do produto/Python, sistema, workspace, configuracao existente, commit local se disponivel, ultimo log e existencia do Python do venv. Consulta PRAGMA quick_check no banco aberto em modo somente leitura, sem criar ou reparar banco. Corrupcao retorna codigo 1. Workspace nao inicializado e mostrado explicitamente.

O status nao executa modelo nem Python do venv e nao usa rede. Existencia de arquivo nao comprova integridade do ambiente. Nao e monitor de processo de IA. Gera um novo log operacional depois da consulta.

## Logs

JSONs exclusivos em WORKSPACE/logs. Incluem comando, sucesso/falha, duracao, UTC e classe do erro. Nao registram argumentos, texto de notas, prompts ou tokens. O caminho e retornado no JSON ou no stderr. Se nao puder gravar o relatorio, a operacao retorna falha. Ajuda, versao e erros de sintaxe nao geram log operacional. Nao ha telemetria, upload ou rotacao automatica.

## Autoload opt-in

```sh
python rpa.py autoload --platform linux
python rpa.py autoload --platform termux
python rpa.py autoload --platform windows
```

Gera templates no workspace sem registra-los no sistema. Atualizacao so entra no template com --auto-update explicitamente. Leia e ajuste o arquivo antes de configurar inicializacao no seu aparelho. Linux: servico de usuario, sem sudo. Termux: exige Termux:Boot instalado e configurado manualmente. Windows: o script PowerShell nao cria tarefa agendada. Sem modelo ou processo permanente nesta versao.

Nenhuma instrucao ativa servicos automaticamente. Nao substitua sua configuracao de inicializacao sem revisar. Venv nao e sandbox de seguranca.
