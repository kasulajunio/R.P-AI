# R.P AI

Repositorio oficial privado de Fabio, conta `kasulajunio`. Motor modular Python baseado no esqueleto fornecido pelo titular. Versao 0.1.0: fundacao funcional, nao produto completo nem certificacao de seguranca. Nome anterior: Fabio Official Core.

> PRIVADO. Uso somente autorizado. Leia [termos](TERMS.md), [licenca proprietaria](LICENSE) e [riscos](docs/RISKS.md). Os avisos nao eliminam obrigacoes previstas em lei.

## Inicio rapido

Python 3.10 ou superior. O nucleo usa apenas a biblioteca padrao, sem pacotes obrigatorios, modelos ou downloads automaticos. A clonagem exige acesso autorizado ao repositorio privado.

```sh
git clone https://github.com/kasulajunio/R.P-AI.git
cd R.P-AI
python engine.py --help
python engine.py --root .core init
python engine.py --root .core doctor
python engine.py --root .core prepare ai --venv
python engine.py --root .core prepare db
python engine.py --root .core note-add "Primeira nota" --body "Texto local sem criptografia"
python engine.py --root .core note-list
python engine.py sha256 README.md
```

No Linux/Termux, use python3 se necessario; no Windows, py -3 pode substituir python. O menu esta em python engine.py; a CLI tambem funciona com python -m official_core. Coloque --root antes do comando.

O nome do pacote Python official_core, a classe MasterEngine e a pasta padrao Fabio_Official_Core foram preservados para compatibilidade. O nome oficial do projeto e R.P AI, e a URL atual e a deste README.

## Funcoes reais e limites

| Modulo | Funciona agora | Ainda nao implementado |
| --- | --- | --- |
| AI_Local_Engine | Estrutura, venv explicito e teste do ambiente | Instalacao ML, inferencia e modelos |
| Crypto_Vault | Avisos e SHA-256 de arquivos pela CLI | Cofre criptografado, carteira e custodia |
| Database_Nexus | Notas SQLite locais com consultas parametrizadas | Criptografia, sincronizacao e multiusuario |
| Gaming_Environment | Configuracao inicial sem execucao | Motor de jogo ou launcher |
| Network_Tunnels | Configuracao desativada em loopback | Tunel, VPN, servidor e proxy |

Preparado nao significa instalado. Venv separa dependencias, nao e sandbox de seguranca. Detectar nvidia-smi nao valida CUDA. Crypto_Vault nao deve receber senhas ou seeds. Configuracoes existentes sao preservadas. Use workspace dedicado e backup.

## Instrucoes e politicas

- [Guia de uso](docs/USAGE.md)
- [IA local e limites](docs/AI_LOCAL.md)
- [Arquitetura](docs/ARCHITECTURE.md)
- [Riscos e controles](docs/RISKS.md)
- [Status verificavel](docs/STATUS.md)
- [Privacidade no perfil GitHub](docs/PROFILE.md)
- [Instrucoes para agentes](AGENTS.md)
- [Seguranca](SECURITY.md)
- [Contribuicao privada](CONTRIBUTING.md)

## Testar de verdade

```sh
python -m unittest discover -s tests -v
python scripts/smoke.py
python scripts/metrics.py
```

O smoke test cria um workspace temporario, prepara os cinco modulos, cria e executa o Python do venv, roda o teste de IA sem PyTorch, valida persistencia SQLite, hash e diagnostico. Nao baixa modelos nem abre rede. A CI repete isso em Linux, Windows e macOS Intel, Python 3.10 e 3.12. Verifique o resultado do commit atual nos checks. Android/Termux e GPU real ainda nao foram testados.

## Propriedade

Titular: Fabio. Oficial e uma identidade declarada pelo titular, sem afiliacao com fornecedores. Nenhuma permissao de publicacao ou redistribuicao e concedida aqui. Dependencias e modelos possuem licencas separadas.
