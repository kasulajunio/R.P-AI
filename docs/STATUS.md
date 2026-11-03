# Status honesto

Versao 0.1.0: fundacao privada baseada no codigo fornecido por Fabio. Estrutura, CLI, validacao de caminhos, venv explicito, hash, notas SQLite e configuracoes iniciais implementados.

O workflow .github/workflows/ci.yml executa testes unitarios, compilacao e criacao real de venv em Linux, Windows e macOS, Python 3.10 e 3.12. Consulte os checks do commit/PR para confirmar o resultado de cada execucao. A presenca deste documento nao significa que todos os testes passaram.

Nao validado aqui: GPU real, CUDA, download de modelos, inferencia, Android/Termux em aparelho real, cofre criptografado, engine de jogos, VPN e tuneis. Os tres ultimos ainda nao sao implementacoes completas. O repositorio e privado, sem vitrine publica criada automaticamente.

Antes de considerar uma nova versao pronta, executar regressao, smoke tests e revisao de riscos, e registrar o commit que foi testado.
