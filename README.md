# Projeto IP

Projeto de Introdução à Programação do curso de Engenharia da Computação 24.2 do Centro de Informática da UFPE.


## Guia de contribuição

### Setup
- Instalem o [uv](https://docs.astral.sh/uv/getting-started/)
- Execute o programa com `uv run main.py`

### Convenções
- Utilizem o snake-case para nomear variáveis.
  ```py
  minha_variavel = 0 # 🟢
  minhaVariavel = 0  # ❌
  minhavariavel = 0  # ❌
  ```
- Executem `uvx ruff format .` para garantir que o código está uniforme e legível.

### Criando um Fork

- Acesse o repositório original no GitHub.
- Clique no botão Fork no canto superior direito.

### Clonando o Repositório Forkado

- Abra o terminal e clone o repositório forkado para sua máquina:
- `git clone https://github.com/seu-usuario/nome-do-repositorio.git`
- Entre no diretório do repositório:
  - `cd nome-do-repositorio`
- Adicione o repositório original como um remote upstream para poder sincronizar depois:
  - `git remote add upstream https://github.com/levydsa/projeto-ip.git`
- Verifique os remotes configurados:
  - `git remote -v`

### Criando e Trocando de Branch

- Sempre comece na branch main ou master e atualize-a antes de criar uma nova branch:
  - `git checkout main`
  - `git pull upstream main`
- Agora, crie e mude para uma nova branch para trabalhar na sua feature ou correção:
  - `git checkout -b minha-nova-branch`

### Fazendo Alterações e Commitando

- Faça suas alterações no código e adicione os arquivos modificados:
  - `git add .`
- Crie um commit com uma mensagem descritiva:
  - `git commit -m "Adiciona nova funcionalidade X"`

### Enviando as Mudanças para o GitHub

- Envie suas mudanças para o repositório forkado:
  - `git push origin minha-nova-branch`

### Abrindo um Pull Request (PR)

- Vá para seu repositório no GitHub.
- Clique no botão Compare & pull request que aparece depois do push.
- Verifique as mudanças e preencha a descrição do PR.
- Clique em Create pull request para enviar sua contribuição.

### Atualizando sua Branch main e Criando uma Nova Branch

Depois que seu PR for revisado e aprovado, atualize sua branch main e crie uma nova branch para um novo trabalho.

- Volte para a main:
  - `git checkout main`
- Pegue as atualizações do repositório original:
  - `git pull upstream main`
- Envie essas atualizações para seu repositório forkado:
  - `git push origin main`
- Criando uma nova branch para o próximo trabalho
  - `git checkout -b outra-nova-branch`

