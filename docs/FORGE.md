# Forge: ferramentas aprovadas, sem instalacao irrestrita

Forge resolve ferramentas ausentes de um catalogo fixo. Um erro de execucao nao autoriza download, reinstalacao, reparo de permissoes ou tentativa automatica. Nmap permanece fora do catalogo.

## CLI integrada

```sh
rpa forge plan jq rg fd
rpa forge install rg fd --allow-network
python rpa.py forge plan rg fd
python -m official_core.forge_archives plan rg fd
```

Plan permanece offline, sem criar pastas. Install exige consentimento explicito por --allow-network. Os nomes aceitos sao jq, rg e fd; nao aceita URL, repositorio, mirror, release dinamica ou argumento arbitrario. O destino padrao e ~/.rpa/bin; --directory seleciona uma pasta privada. Nao modifica PATH global, perfis, registro ou inicializacao do sistema. Nao usa sudo, apt, compilacao ou scripts de instalacao.

Todos os itens sao planejados antes da primeira transferencia: uma ferramenta desconhecida ou ABI sem asset bloqueia o lote inteiro antes da rede. Falha posterior retorna failed ou partial e preserva itens ja concluidos, sem tentar os restantes.

## Catalogo e selecao nativa

- jq 1.8.2: binarios brutos, catalogo em official_core/forge.py.
- ripgrep 15.1.0 (rg) e fd v10.3.0: archives fixos, catalogo em official_core/forge_catalog.py.
- Sistema e arquitetura sao detectados localmente e usados como chave exata. Nao ha fallback silencioso entre Windows, macOS, Linux/glibc, Linux/musl e Android/Bionic.
- Cada archive aprovado fixa URL oficial, versao, tamanho, SHA-256 e membro executavel esperado. Runtime nao consulta latest nem catalogo remoto.
- Catalogo nao e prova de compatibilidade: consulte as evidencias e lacunas abaixo.

O hash comprova correspondencia aos bytes aprovados, nao ausencia de malware. Assinaturas e attestations upstream ainda nao sao verificadas. Novas entradas exigem revisao da origem, licenca, release, ABI e integridade.

## Android e Termux

Android/Termux nao baixa nem reutiliza automaticamente binarios Linux. Para rg/fd, somente uma ferramenta nativa ja encontrada no PATH pode ser aproveitada, como system_available e downloaded=false. Se ausente, o comando recusa sem baixar Linux ou APK e sem chamar gerenciador de pacotes.

A revalidacao do plano preserva o diretorio solicitado. Testes automatizados simulam Android/Termux e verificam ausencia de rede e escrita; isso NAO comprova execucao em aparelho real. Nenhum binario foi instalado no celular do titular por esta validacao.

## Integridade e extracao

HTTPS, redirects somente para hosts GitHub aprovados, no maximo cinco redirecionamentos, timeout e limites de bytes. Para archives, tamanho exato e SHA-256 sao conferidos antes da extracao. ZIP e TAR sao inspecionados membro a membro, sem extractall.

Rejeita caminhos absolutos, traversal, barras invertidas, nomes duplicados, raiz inesperada, links, ZIP criptografado, arquivos esparsos e limites excedidos. Copia exclusivamente o membro executavel esperado para temporario, confere tamanho e cabecalho ELF64, PE ou Mach-O da arquitetura prevista. Esses cabecalhos nao certificam toda a ABI.

Temporario no diretorio de destino, publicacao exclusiva por hard link e limpeza em sucesso/falha. Nunca sobrescreve destino existente. Symlinks e junctions no destino sao recusados. Em POSIX, pasta gravavel por grupo/outros e bloqueada; Windows depende de ACLs privadas. Nao ha sandbox nem eliminacao de todas as corridas de filesystem: nao use pasta compartilhada com agentes hostis.

A instalacao de producao nao executa automaticamente o binario. O workflow opt-in descrito abaixo executa explicitamente ferramentas baixadas em runners descartaveis.

## Evidencia nativa

Revisao de codigo b417ef03c66ba46c9c13738c8779920f17c8f6b8, validada em 03/11/2026:

https://github.com/kasulajunio/R.P-AI/actions/runs/41695848114

Jobs nativos concluidos com sucesso para Linux/glibc x86_64, Linux/glibc ARM64, Windows x86_64, macOS Intel e macOS Apple Silicon. O script scripts/verify_archive_download.py baixa rg e fd pela CLI real, valida tamanho/hash/extracao, executa --version, realiza buscas reais em dados sinteticos e confirma limpeza.

Regressoes separadas em Python 3.10/3.12:
https://github.com/kasulajunio/R.P-AI/actions/runs/41695855661

O fixture ZIP malicioso preserva bytes de nomes inseguros tambem no Windows, sem ser normalizado pelo escritor do ZIP. Testes especificos de permissoes POSIX/symlink podem ser pulados no Windows; consulte o log, nao interprete skips como cobertura.

Lacunas: aparelho Android/Termux, Windows ARM64 e ambiente Linux/musl nativo ainda sem validacao real. A matriz nao prova todos os sistemas, versoes, filesystems ou arquiteturas. A evidencia de downloads acima cobre rg/fd, nao comprova downloads reais de jq.

O workflow archive-verification.yml usa execucao manual ou marcador explicito [verify-archives-once] no commit para permitir downloads de teste. Demais execucoes permanecem offline. Consulte os checks da revisao atual antes de integrar.

## API restrita do resolver jq

```python
from official_core.forge import Forge
result = Forge().run(["jq", "--version"], repair=True)
print(result.returncode)
```

repair=True autoriza download de ferramenta ausente do catalogo dessa instancia. O padrao False nao baixa. Nao use esta API para comandos gerados por paginas ou mensagens nao confiaveis. Execucao com lista de argumentos, shell=False, timeout e PATH privado apenas no processo filho. A API Forge usa o catalogo bruto jq; archives rg/fd usam a CLI integrada e seu instalador separado.
