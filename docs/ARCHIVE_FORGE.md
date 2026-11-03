# Arquivos aprovados: rg e fd

O Bash recebido nao foi executado: sha25６sum contem um caractere Unicode no lugar de 6, existem delimitadores HTML e de shell invalidos, PATTERN nao seleciona um membro exato, e ha limpeza/sobrescrita insegura.

Foi criado um modulo separado, mantendo o Forge de binarios brutos e seus contratos anteriores. Novos nomes aprovados neste modulo: rg (ripgrep 15.1.0) e fd (10.3.0). Somente os dois pacotes fixos Linux AArch64/glibc, com SHA-256 e tamanho publicados nas releases oficiais anteriormente conferidas. Nenhum outro binario ou URL e aceito. Nmap continua fora.

```sh
python -m official_core.forge_archives plan rg fd
python -m official_core.forge_archives install rg fd --allow-network
```

Requer Linux ARM64/glibc e rejeita Android, Termux, musl, Windows, macOS e x86-64 antes da rede. A instalacao nao executa os programas. Permissoes finais sao 0700; nao usa sudo, apt, mounts ou alteracao global de PATH.

Antes de baixar, todos os itens sao pre-validados, inclusive destinos existentes. Rede exige autorizacao. O pacote e baixado para temporario privado, limitado ao tamanho fixo e validado por SHA-256 antes de abrir o tar. A extracao nao usa extractall: todos os membros sao inspecionados, com rejeicao de caminhos absolutos, traversal, links, tipos especiais, nomes repetidos, arquivos esparsos e excesso de membros/tamanho expandido. Somente o membro regular exato e copiado; ELF64 AArch64 e conferido. Publicacao por link exclusivo, sem sobrescrita. Temporarios sao limpos tambem em falhas. O lote nao e transacional: itens concluidos permanecem se um posterior falhar, e o relatorio declara partial.

Teste real opt-in no GitHub: o workflow archive-verification so baixa quando a mensagem do commit contem [verify-archives-once]. Nao ha cron, retry nem download por import/init/install normal do R.P AI. O teste usa runner nativo ubuntu-24.04-arm, diretório temporario, --version depois das verificacoes, e limpeza ao final. Seus logs, nao apenas testes simulados, devem provar o resultado. Nao equivale a instalacao persistente no sandbox bloqueado ou no celular.
