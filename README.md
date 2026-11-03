# Fabio Official Core

Repositorio oficial privado de Fabio, conta `kasulajunio`. Motor modular Python baseado no esqueleto fornecido pelo titular. Versao 0.1.0: fundacao funcional, nao produto completo nem certificacao de seguranca.

> PRIVADO. Uso somente autorizado. Consulte [termos](TERMS.md), [licenca proprietaria](LICENSE) e [riscos](docs/RISKS.md) antes de executar. Nenhuma clausula elimina obrigacoes legais.

## Inicio rapido

Requer Python 3.10 ou superior. O nucleo usa apenas a biblioteca padrao. Sem conta adicional, telemetria, downloads de modelos ou pacotes obrigatorios. A clonagem exige acesso autorizado a este repositorio privado.

```sh
git clone https://github.com/kasulajunio/fabio-official-core.git
cd fabio-official-core
python engine.py --help
python engine.py --root .core init
python engine.py --root .core doctor
python engine.py --root .core prepare ai --venv
python engine.py --root .core prepare db
python engine.py --root .core note-add "Primeira nota" --body "Texto local sem criptografia"
python engine.py --root .core note-list
python engine.py sha256 README.md
```

No Linux/Termux, use `python3` se esse for o nome instalado. No Windows, `py -3` pode substituir `python`. O menu interativo original esta em `python engine.py`; a CLI tambem funciona com `python -m official_core`. Coloque `--root` antes do comando.

O menu nao cria venv nem baixa nada automaticamente. O argumento `--venv` e explicito. A pasta padrao e `./Fabio_Official_Core`, sem divulgar o hostname no nome. Arquivos existentes de configuracao nao sao sobrescritos. Use um workspace dedicado e backup.

## O que realmente funciona

| Modulo | Implementado | Nao implementado |
| --- | --- | --- |
| AI_Local_Engine | Pasta, venv opcional e teste de disponibilidade de PyTorch | Instalador ML, inferencia e download de modelos |
| Crypto_Vault | Avisos e comando SHA-256 de arquivos | Cofre criptografado, carteira e custodia |
| Database_Nexus | SQLite, inclusao/listagem de notas e consultas parametrizadas | Criptografia, sincronizacao e multiusuario |
| Gaming_Environment | Configuracao inicial local sem execucao | Motor de jogo ou launcher |
| Network_Tunnels | Configuracao desativada, loopback | Tuneis, VPN, servidor ou proxy |

Preparado nao significa instalado. Venv separa dependencias Python, nao isola malware do sistema operacional. Detectar `nvidia-smi` nao valida CUDA nem compatibilidade de bibliotecas. O modulo com nome Crypto_Vault NAO deve receber senhas ou seeds.

## Documentacao

- [Guia de uso e exemplos](docs/USAGE.md)
- [IA local, limites de hardware e instalacao consciente](docs/AI_LOCAL.md)
- [Arquitetura e extensoes](docs/ARCHITECTURE.md)
- [Riscos e responsabilidades](docs/RISKS.md)
- [Status e limites de validacao](docs/STATUS.md)
- [Perfil GitHub e privacidade](docs/PROFILE.md)
- [Instrucoes para agentes de IA](AGENTS.md)
- [Politica de seguranca](SECURITY.md)
- [Como contribuir](CONTRIBUTING.md)

## Testes

```sh
python -m unittest discover -s tests -v
python -m compileall -q official_core engine.py tests
python scripts/metrics.py
```

A CI valida Linux, Windows e macOS com Python 3.10 e 3.12, incluindo uma criacao real de venv. Veja os resultados da execucao, nao trate a existencia do workflow como prova de aprovacao. Android/Termux nao esta na matriz automatizada. Nenhum teste baixa modelos, instala PyTorch ou testa GPU real.

## Propriedade e acesso

Titular identificado neste projeto: Fabio. Repositorio oficial significa identidade declarada pelo titular, sem afiliacao com GitHub, Microsoft, NVIDIA, PyTorch ou outros fornecedores. Nenhuma permissao de redistribuicao publica e concedida por este README. Licencas de dependencias e modelos permanecem separadas.
