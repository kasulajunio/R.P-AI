# Forge multiplataforma

Solicitacao do titular: usar R.P AI em todos os sistemas. Esta revisao amplia o escopo sem prometer compatibilidade universal. O suporte depende do sistema, CPU, libc, permissao e disponibilidade do programa nativo. O codigo Python e o download de rg/fd sao camadas distintas.

## Catalogo fixo de rg/fd

- Linux glibc x86_64 e ARM64: ambos cadastrados. rg x86_64 usa o pacote upstream musl estatico.
- Linux musl x86_64: ambos cadastrados. ARM64: apenas fd; rg nao tem asset correspondente nessa release.
- macOS Intel e Apple Silicon: ambos cadastrados, Mach-O64 da CPU exata.
- Windows x86_64 e ARM64: ambos cadastrados em ZIP, PE da CPU exata. ARM64 precisa teste nativo separado.
- Android/Termux: aceita rg/fd nativos ja existentes no PATH; nao baixa pacotes Linux e nao instala APKs. Ausencia resulta em recusa sem rede. Instalacao dos pacotes nativos do Termux e separada, por iniciativa do titular. Nao foi validado em aparelho.
- iOS, BSD, 32 bits, arquiteturas e ABIs nao listadas: sem asset aprovado. Nao ha fallback silencioso ou promessa de suporte.

## Uso

`python rpa.py forge plan rg fd` inspeciona sem rede nem criacao de pastas.

`python rpa.py forge install rg fd --allow-network` autoriza somente os downloads fixos aplicaveis ao host. No Windows, python pode ser substituido pelo lancador `py -3`. O CLI e Python, nao exige Bash. Nao pede sudo nem altera PATH global.

Tamanho, SHA-256, versao, URL HTTPS oficial e nome interno exato sao fixados no codigo. Todos os membros do pacote sao inspecionados; traversal, caminhos absolutos, duplicatas, caracteres de controle, ADS, symlinks, arquivos especiais e excesso de tamanho sao recusados. ZIP e tar.gz sao lidos sem extractall. Somente um binario regular e copiado. O cabecalho confirma ELF/PE/Mach-O e CPU, nao certifica o programa nem o aparelho. Instalacao usa temporario privado e publicacao exclusiva, sem sobrescrever. ACLs do Windows continuam responsabilidade do ambiente.

## Evidencia

O workflow Approved archive verification testa downloads reais, integridade, extracao, --version, busca de conteudo e busca de arquivo em runners nativos Linux x86_64/ARM64, Windows x86_64 e macOS Intel/ARM64. Consulte a execucao do commit atual: configuracao de matrix nao equivale a teste aprovado. Musl real, Windows ARM64 e dispositivo Android/Termux nao sao cobertos por essa matrix. Nenhuma instalacao foi feita no celular do titular.

Fontes fixas: https://github.com/BurntSushi/ripgrep/releases/tag/15.1.0 e https://github.com/sharkdp/fd/releases/tag/v10.3.0. Metadados de tamanho e digest obtidos da API oficial das duas releases. Pacotes Termux: https://github.com/termux/termux-packages/tree/master/packages/ripgrep e https://github.com/termux/termux-packages/tree/master/packages/fd.
