# 🤖 Diretrizes e Regras de Desenvolvimento do Projeto

Este arquivo define as regras de desenvolvimento e os padrões arquiteturais que todos os agentes de IA devem seguir estritamente ao trabalhar neste workspace.

---

## 🏗️ 1. Arquitetura e Design (Clean Architecture & DDD)
- **Isolamento de Domínio (`domain/`):** As entidades de domínio e regras de negócio puras devem ser escritas em Python puro (utilizando `dataclasses` ou classes padrão). Elas **nunca** devem importar dependências externas ou SDKs do Google Cloud (como `google.cloud.firestore` ou `google.cloud.pubsub`).
- **Inversão de Dependência:** Todo acoplamento com serviços externos (banco de dados, mensageria, IA) deve ser feito através de portas (interfaces/classes abstratas) definidas no domínio ou nos casos de uso, e implementado na camada de infraestrutura (`infrastructure/`).
- **Casos de Uso (`use_cases/`):** Devem coordenar a lógica da aplicação, recebendo as interfaces por injeção de dependência no construtor.

---

## 🐍 2. Padrões de Código Python
- **Tipagem de Dados:** O uso de *Type Hints* (ex: `def processar(chamado: Chamado) -> None:`) é obrigatório para todas as funções e métodos.
- **Tratamento de Erros:** Exceções devem ser capturadas de forma explícita. Evitar blocos `try: ... except: pass`. Erros de infraestrutura devem ser traduzidos para exceções de domínio ou tratados de forma resiliente.
- **Logs:** Utilizar o módulo padrão `logging` do Python para registrar eventos importantes (rastreabilidade). Nunca utilizar `print()`.

---

## 💶 3. Governança e Custo Zero (GCP Free Tier)
- **Segurança de Credenciais:** Nunca expor chaves de API (como a chave do Google AI Studio) diretamente no código. Elas devem ser injetadas exclusivamente via variáveis de ambiente (`os.environ`) ou lidas do GCP Secret Manager.
- **Eficiência de Computação:** Escrever código eficiente para garantir que o tempo de execução das Cloud Functions seja o menor possível, minimizando o consumo de cota de CPU-segundo gratuita.
- **Evitar Loops Infinitos:** Garantir que todos os fluxos de mensagens Pub/Sub tenham confirmações (Acks) tratadas corretamente para evitar o reprocessamento infinito e estouro de cota.

---

## 🧪 4. Testabilidade e Mocks
- Todo código de infraestrutura deve ser mockável. Deve ser possível executar e validar a lógica de negócios localmente sem requisições reais à nuvem.
