# R.P AI: status verificavel

Versao 0.1.0: fundacao privada baseada no codigo fornecido por Fabio. Nome anterior Fabio Official Core; pacote official_core e pasta padrao foram preservados por compatibilidade.

Implementado: estrutura, CLI, validacao de caminhos, venv explicito, hash SHA-256, notas SQLite e configuracoes iniciais.

No commit d56c8c3aec089dc882e5f3dd876e58ae7dcdd2eb, os checks Linux e Windows passaram com Python 3.10 e 3.12. Os jobs macos-latest ficaram aguardando runners disponiveis, sem executar; isso nao prova nem falha nem aprovacao no macOS.

A revisao atual troca somente a imagem macOS para macos-15-intel e acrescenta smoke test em processos reais: inicializacao repetida, preparacao de cinco modulos, criacao/execucao/reutilizacao do venv, teste de IA sem PyTorch, persistencia SQLite, hash e rede desativada. Consulte os checks do commit atual antes de afirmar aprovacao final.

Nao validado: GPU/CUDA reais, modelos, inferencia e Android/Termux em aparelho real. Cofre criptografado, engine de jogos e tuneis nao sao implementacoes completas. Nenhuma alteracao de visibilidade publica foi feita. Documentos legados que mencionem Fabio Official Core referem-se ao mesmo projeto, agora R.P AI.
