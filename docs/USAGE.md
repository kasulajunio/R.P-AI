# Guia de uso

## Requisitos

Python 3.10+ com SQLite e venv. Nao ha dependencia pip obrigatoria. Nao use root ou Administrador. Clone com uma conta autorizada; nunca cole token no codigo ou na URL do Git. Leia os termos antes de conceder acesso a outra pessoa.

## Comandos

```sh
python -m official_core --help
python -m official_core modules
python -m official_core --root .core init
python -m official_core --root .core doctor
python -m official_core --root .core prepare ai
python -m official_core --root .core prepare ai --venv
python -m official_core --root .core prepare crypto
python -m official_core --root .core prepare db
python -m official_core --root .core prepare gaming
python -m official_core --root .core prepare network
python -m official_core --root .core note-add "Teste" --body "Exemplo nao sensivel"
python -m official_core --root .core note-list --limit 10
python -m official_core sha256 README.md
```

Os numeros de 1 a 5 tambem funcionam em prepare. Saida normal em JSON; erro operacional retorna codigo 1. Erros de argumentos retornam o codigo padrao do argparse. Nenhum comando inicia tunel ou instala PyTorch.

## Teste do ambiente de IA

Depois de prepare ai --venv, em Linux/macOS:

```sh
.core/AI_Local_Engine/ai_env/bin/python .core/AI_Local_Engine/run_ai_test.py
```

PowerShell, Windows:

```powershell
& .\.core\AI_Local_Engine\ai_env\Scripts\python.exe .\.core\AI_Local_Engine\run_ai_test.py
```

Nao precisa ativar o ambiente nem alterar a politica de execucao do PowerShell. PyTorch ausente e um resultado esperado nesta versao.

## Termux e Android

O modulo de arquivos, hash e SQLite pode funcionar se o Python incluir os modulos necessarios. Android/Termux e experimental e nao foi validado em aparelho real nesta entrega. Venv, ensurepip e wheels ML podem ser indisponiveis nessa distribuicao. Nao instale pacotes para desktop esperando compatibilidade garantida no Android. Sem PC obrigatorio para guardar o projeto no GitHub.

## Dados, backup e atualizacao

O banco fica em Database_Nexus/notes.sqlite3, dentro do workspace. Feche todas as instancias antes de copiar o workspace para backup; nao use notas para segredos. O programa nao sincroniza dados. Faca backup antes de atualizar codigo ou dependencias. Configuracoes existentes sao preservadas, nao migradas automaticamente. Se houver ambiente virtual incompleto, ele e recusado: preserve a pasta e escolha outro workspace.

## Remocao

O programa nao possui comando destrutivo de limpeza. Revise manualmente quais dados devem ser preservados antes de apagar o workspace. Apagar o repositorio nao revoga credenciais externas nem elimina backups. Nunca publique o workspace, modelos, banco, .env ou chaves.
