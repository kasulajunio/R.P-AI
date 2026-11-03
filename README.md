# R.P AI

Projeto de Fabio: ferramentas locais em Python para notas, tarefas, SQLite, diagnóstico, backup, integridade e planejamento de ferramentas pelo Forge.

## Todos os comandos

**[Abrir o guia completo de comandos](docs/COMANDOS.md)**

O guia traz exemplos, opções, instalação no Alpine/Acode, comandos com acesso à rede e alertas para exclusão de dados. A referência é o código da versão 0.2.0 no commit `8c378b7`, não uma promessa de recursos futuros.

## Onde está o código

Esta branch principal contém a documentação de entrada. O código em desenvolvimento está na branch [feat/official-foundation](https://github.com/kasulajunio/R.P-AI/tree/feat/official-foundation).

- [Código exato usado como referência do guia](https://github.com/kasulajunio/R.P-AI/tree/8c378b7691979ca151c5a5aea0ed7ae010ba57ff)
- [Testes isolados para Alpine/Acode](https://github.com/kasulajunio/R.P-AI/tree/test/alpine-install-smoke)
- [Recuperação nativa testada em Alpine 3.21 ARM](https://github.com/kasulajunio/R.P-AI/actions/runs/41733667718)

## Limites reais

Nesta revisão não há inferência implementada nem comando de conversa com um modelo. Preparar um módulo não implementa automaticamente uma IA, um cofre criptografado, um jogo ou um túnel de rede. Venv não é sandbox. Os comandos não baixam modelos nem ativam serviços automaticamente.

Não execute todos os exemplos em sequência. Leia os avisos de rede, exclusão e caminhos antes de usar.

## Licença

O código de referência usa [MIT, Copyright 2026 Fabio](https://github.com/kasulajunio/R.P-AI/blob/8c378b7691979ca151c5a5aea0ed7ae010ba57ff/LICENSE). Consulte também os [termos dessa revisão](https://github.com/kasulajunio/R.P-AI/blob/8c378b7691979ca151c5a5aea0ed7ae010ba57ff/TERMS.md).
