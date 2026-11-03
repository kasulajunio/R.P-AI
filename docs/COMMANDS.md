# Comandos que fazem trabalho real

Use Python 3.10+. Nos exemplos, python pode ser substituido por python3 ou py -3 conforme docs/TERMINALS.md. Coloque --root antes do comando. Nao e preciso instalar o pacote com pip para executar da pasta do projeto.

```sh
python engine.py --root .core init
python engine.py --root .core note-add "Projeto" --body "Primeiro rascunho"
python engine.py --root .core note-get 1
python engine.py --root .core note-search "rascunho"
python engine.py --root .core note-update 1 --title "Projeto revisado" --body "Segundo rascunho"
python engine.py --root .core note-list --limit 10
python engine.py --root .core note-export minhas-notas.json
python engine.py --root .core task-add "Revisar documentacao"
python engine.py --root .core task-list --state open
python engine.py --root .core task-done 1
python engine.py --root .core task-list --state done
python engine.py --root .core task-done 1 --reopen
python engine.py --root .core db-check
python engine.py --root .core db-backup backup-01.sqlite3
python engine.py sha256 README.md
```

IDs acima pressupoe workspace novo; use os IDs retornados no seu caso. Tarefas sao registros locais, nao lembretes, automacoes ou cron. Busca usa substring do SQLite, nao inferencia de IA, e case-folding de Unicode nao e garantido.

Exportacoes ficam em Database_Nexus/exports e backups em Database_Nexus/backups dentro do workspace. Sao criados sem sobrescrever arquivos existentes. O backup usa a API SQLite e verifica quick_check; nao equivale a backup de todos os arquivos do projeto. Nao ha restauracao automatica nesta versao. Guarde uma copia fora do aparelho e valide recuperacao antes de depender dela.

## Exclusao explicita

O comando abaixo remove apenas a nota indicada, de forma persistente. Faca backup antes se precisar recupera-la. Sem --confirm, a exclusao e recusada.

```sh
python engine.py --root .core note-delete 1 --confirm
```

## Limites e seguranca

Titulos: ate 200 caracteres. Notas: texto ate 10000 caracteres. Listagens: 1 a 100 registros. Exportacao: ate 10000 notas. Consultas usam parametros, nao concatenam entrada em SQL. Caminhos de exportacao e backup aceitam somente nomes simples. Notas, tarefas, backups e JSON NAO sao cifrados. Em workspace compartilhado com agentes hostis, checagens de caminho nao eliminam corridas de filesystem; use isolamento do sistema operacional.

## O que ainda falta

Inferencia com modelo real, chat de IA, cofre criptografado, motor de jogos e tuneis nao foram implementados. Preparar uma pasta nunca deve ser anunciado como implementar essas funcoes. O repositorio oferece ferramentas locais funcionais e pontos de expansao, nao uma suite de IA concluida.
