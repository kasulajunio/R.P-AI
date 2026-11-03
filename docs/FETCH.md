# Entrada Bash segura para o Forge

O downloader recebido nao foi incorporado: estava incompleto, anunciava SHA-256 sem compara-lo e encadeava chmod com echo por pipe, podendo mascarar falha. Escrever direto no destino tambem arriscava sobrescrita.

Use o motor existente, sem duplicar regras de seguranca:

```sh
bash scripts/fetch plan jq
bash scripts/fetch install jq --allow-network
```

Execute dentro do repositorio. Por caminho absoluto, o wrapper tambem funciona a partir de outra pasta. Requer Bash e Python 3.10+; nao instala dependencias do sistema nem exige chmod no wrapper. Sem Bash, use python rpa.py forge plan jq.

Plan nao baixa nem executa ferramentas. Install exige consentimento e delega ao Forge: catalogo fixo, HTTPS, SHA-256, verificacao de formato, arquivo temporario e publicacao sem sobrescrita. Preserva saida e codigo de retorno, sem mensagem extra de sucesso. Nao executa o binario instalado nem altera PATH global. Veja FORGE.md e FORGE_CLI.md.

Nao aceita URL, nome de arquivo ou checksum arbitrarios. Somente jq esta aprovado; Android/Termux nao possui asset aprovado. Nao contorna limite de requisicoes ou indisponibilidade do ambiente remoto.

Novos testes cobrem sintaxe Bash, caminhos com espacos, argumentos literais, retorno de erro, uso sem argumentos e instalacao sem consentimento. Rodam em POSIX; os testes existentes cobrem a CLI Python em multiplas plataformas. Nao comprovam download real nem funcionamento no celular.
