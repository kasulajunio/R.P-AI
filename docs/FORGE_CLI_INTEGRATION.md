# Forge integrado ao comando rpa

```sh
rpa forge plan rg fd
rpa forge install rg fd --allow-network
rpa forge plan jq rg fd
```

Sem instalar o pacote Python, a mesma entrada oficial pode ser testada com python rpa.py forge, a partir da raiz do repositorio. O comando instalado rpa aponta para official_core.console:main, exatamente a funcao usada por rpa.py.

A CLI aceita um ou varios nomes do catalogo fixo, nunca URLs ou versoes arbitrarias. Lotes mistos pre-validam todos os itens antes da primeira rede. rg e fd seguem exclusivamente o instalador restrito de arquivos, com Linux ARM64/glibc, tamanho e SHA-256 fixos, extracao do membro exato, verificacao ELF e publicacao sem sobrescrita. jq conserva seu resolvedor anterior; se ja estiver no PATH, o resultado e system_available, nao downloaded. O JSON legado de um unico jq foi preservado.

Plano e somente leitura, sem workspace, banco, relatorios nem rede. Install exige --allow-network. Duplicatas, nomes desconhecidos e ABI nao aprovada abortam antes de baixar. Em falha parcial, itens concluidos permanecem, status partial e codigo de saida 1; nao ha retry nem rollback destrutivo.

O teste real opt-in chama python rpa.py forge install rg fd em Linux ARM64 nativo, em pasta temporaria. Confere relatorio de downloads, --version, busca real de conteudo com rg, busca real de nome com fd, ausencia de temporarios residuais e limpeza final. Nao comprova compatibilidade Android/Termux nem instala no celular. Nmap continua fora do catalogo.
