# Sistema de Gestão de Dados (SGD) - Cadeia de Supermercados

Bem-vindo ao repositório do **Sistema de Gestão de Dados (SGD)**, um projeto desenvolvido para armazenar e gerir dados de uma cadeia de supermercados. Este repositório contém o código-fonte, scripts e documentação necessária para instalação e utilização do sistema.

---

## 📝 Sobre o Projeto

O projeto consiste no desenvolvimento de um sistema capaz de:
- Armazenar características e operações de um negócio de supermercados.
- Gerir operações com diversos endpoints para consulta, inserção, atualização e remoção de dados.
- Garantir integridade, segurança e eficiência no tratamento de dados.

O projeto foi desenvolvido por:
- **André Cunha**

---

## 🛠️ Funcionalidades

- **CRUD Completo:** Possibilidade de criar, consultar, atualizar e eliminar dados relacionados a produtos, clientes, compras, entre outros.
- **Encriptação de Palavras-passe:** Para maior segurança, as palavras-passe são encriptadas e armazenadas em variáveis de ambiente.
- **Controle de Transações:** Commit realizado apenas após a execução bem-sucedida de todas as operações.
- **Endpoints Intuitivos:** Implementação de 12 endpoints e uma landing page para facilitar o acesso e interação com a base de dados.

---

## 📁 Estrutura do Projeto

- **`create_tables.py`:** Script para criação das tabelas no PostgreSQL.
- **`ETL.py`:** Script para a extração, transformação e carregamento dos dados fornecidos.
- **`main.py`:** Contém os endpoints e a lógica principal do sistema.
- **`postman.json`:** Coleção de endpoints para teste no Postman.

---

## 🚀 Instalação

Siga os passos abaixo para instalar o sistema:

1. Faça o **download** ou clone este repositório.
   ```bash
   git clone https://github.com/andreecunha/SuperMarketDB.git
