# Forge: fallback aprovado, nao instalador irrestrito

O texto de que qualquer erro vira download e depois funciona nao e correto. Falha pode indicar permissao, dependencia, ABI, configuracao, rede ou defeito do proprio programa. Forge so resolve ausencia; nao baixa de novo porque um comando retornou erro.

## Interface pronta para testar

```sh
python -m official_core.forge plan jq
python -m official_core.forge install jq --allow-network
```

Plan nao usa rede nem cria pastas. Install requer autorizacao explicita de rede, baixa somente o asset aprovado e nao executa o programa. Destino padrao ~/.rpa/bin; --directory escolhe pasta privada. Nao modifica .bashrc, perfil PowerShell, registro ou PATH global. O comando principal rpa run continua dedicado ao nucleo; este modulo e separado e nao intercepta todos os comandos do sistema.

## API para automacao restrita

```python
from official_core.forge import Forge
result = Forge().run(["jq", "--version"], repair=True)
print(result.returncode)
```

repair=True autoriza o download de uma ferramenta ausente do catalogo previamente aprovado, sem perguntar novamente naquela chamada. False e o padrao. Execucao usa caminho resolvido, lista de argumentos, shell=False e timeout. PATH privado vale somente para o processo filho. Falha de execucao e retornada/propagada sem novo download ou retry automatico. Nunca use esse recurso para executar comandos gerados sem revisao a partir de paginas ou mensagens nao confiaveis.

## Catalogo inicial

Somente jq 1.8.2, da release https://github.com/jqlang/jq/releases/tag/jq-1.8.2. URLs e digests SHA-256 foram consultados na API oficial e fixados no codigo; nao ha busca aberta, latest, autoupdate ou catalogo remoto mutavel. Linux glibc, macOS e Windows, x86_64/ARM64, possuem assets cadastrados. Nao ha asset aprovado para Android/Termux, Linux musl ou outras arquiteturas nesta revisao. Ferramenta ja instalada pelo sistema pode ser usada normalmente. Nao confundir ARM Linux com Android/Bionic.

Novas ferramentas exigem revisao do repositorio de origem, licenca, release, ABI e checksum antes de alterar CATALOG. Um host GitHub permitido nao torna qualquer repositorio confiavel. O catalogo revisado constitui a lista de autorizacao.

## Controles

HTTPS, redirects apenas para hosts de assets GitHub, limite de cinco redirecionamentos, timeout por operacao de rede e teto de 64 MiB. SHA-256 obrigatorio antes de chmod, validacao basica de cabecalho de binario, publicacao exclusiva sem sobrescrita e descarte do temporario em falha. Diretorios com symlink/junction sao recusados; pasta POSIX nao pode permitir escrita de grupo/outros. Windows depende tambem de ACLs locais.

Nao extrai ZIP/tar, compila, instala bibliotecas, chama apt/sudo ou executa scripts de instalacao. Instalacao nao executa teste de versao por conta propria. Execucao de programa baixado ocorre somente via chamada explicita a run ou pelo titular. Hash demonstra correspondencia ao catalogo, nao ausencia de malware; assinatura/attestation ainda nao verificada. Checagem de cabecalho nao certifica arquitetura nem compatibilidade em aparelho real.

## Limites de seguranca e validacao

Sem sandbox, rotacao de versoes ou auditoria profissional. Use pasta privada, nao compartilhada com agentes hostis; checagens de caminho nao eliminam toda corrida de filesystem. Nao ha lock global: instalacoes concorrentes nao sobrescrevem destino, uma delas pode falhar. Para atualizar, preserve/revise a versao anterior; nao ha substituicao silenciosa.

Testes offline usam respostas sinteticas e subprocessos simulados. Eles cobrem download, hash, integridade, limite, rejeicoes, redirecionamentos e comportamento de falha, mas nao provam que jq real foi baixado ou executado, nem validam Android. Consulte workflow Forge e CI do commit atual. Nenhum binario real foi instalado no dispositivo do titular.
