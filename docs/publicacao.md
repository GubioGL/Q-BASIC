# Publicação no PyPI

O Q-BASIC é publicado no PyPI com o nome **`Q-BASIC`** (`pip install Q-BASIC`); o
módulo importado continua sendo `qbasic` (`import qbasic as qb`).

A publicação é **automática**: ao publicar uma *release* no GitHub, o workflow
[`.github/workflows/publicar.yml`](../.github/workflows/publicar.yml) roda todos os testes,
gera o pacote e envia ao PyPI. Não é preciso guardar senha nem token no GitHub: o envio
usa o **Trusted Publishing** do PyPI (autenticação OIDC entre GitHub e PyPI).

## Configuração inicial (uma vez só)

A versão 0.0.3 foi enviada manualmente, então o PyPI ainda não confia neste repositório.
Para autorizar:

1. Entre em <https://pypi.org> com a conta dona do projeto `Q-BASIC`.
2. Abra **Your projects → Q-BASIC → Manage → Publishing**
   (<https://pypi.org/manage/project/Q-BASIC/settings/publishing/>).
3. Em **Add a new publisher → GitHub**, preencha:

   | Campo | Valor |
   |---|---|
   | Owner | `GubioGL` |
   | Repository name | `Q-BASIC` |
   | Workflow name | `publicar.yml` |
   | Environment name | `pypi` |

4. Clique em **Add**.
5. *(Opcional, recomendado)* No GitHub, em **Settings → Environments → pypi**, ative
   **Required reviewers** e adicione você mesmo: assim cada publicação espera a sua
   aprovação com um clique antes de ir ao PyPI. O ambiente `pypi` é criado
   automaticamente na primeira execução do workflow, se ainda não existir.

## Como lançar uma nova versão

1. Atualize a versão em [`src/qbasic/_version.py`](../src/qbasic/_version.py) seguindo o
   [versionamento semântico](https://semver.org/lang/pt-BR/):
   `0.1.0 → 0.1.1` (correções), `0.1.0 → 0.2.0` (novidades),
   `0.x → 1.0.0` (API estável).
2. Faça o merge na `main` e confira se o workflow **Testes** está verde.
3. No GitHub: **Releases → Draft a new release**.
   - **Tag**: `v` + a versão, por exemplo `v0.1.0` (crie a tag a partir da `main`).
   - **Título** e **descrição**: o que mudou (o botão *Generate release notes* ajuda).
4. Clique em **Publish release**.
5. Acompanhe em **Actions → Publicar no PyPI**. Ao terminar, a nova versão aparece em
   <https://pypi.org/project/Q-BASIC/> e pode ser instalada com
   `pip install -U Q-BASIC`.

O workflow **para com erro** se a tag não corresponder à versão de `_version.py`
(por exemplo, tag `v0.2.0` com `__version__ = "0.1.0"`), para evitar publicar o número
errado.

> O PyPI não permite reenviar a mesma versão. Se algo der errado depois do envio,
> corrija e lance uma nova versão (por exemplo, `0.1.1`).

## Alternativa: token de API

Se preferir não usar o Trusted Publishing:

1. Crie um token em <https://pypi.org/manage/account/token/> com escopo restrito ao
   projeto `Q-BASIC`.
2. No GitHub, em **Settings → Secrets and variables → Actions**, crie o segredo
   `PYPI_API_TOKEN` com o token.
3. No final de `publicar.yml`, troque o último passo por:

   ```yaml
   - uses: pypa/gh-action-pypi-publish@release/v1
     with:
       password: ${{ secrets.PYPI_API_TOKEN }}
   ```

## Publicação manual (emergência)

```bash
pip install build twine
python -m build
twine check --strict dist/*
twine upload dist/*
```

## Sobre o nome no PyPI

`Q-BASIC` já pertence ao projeto e continua sendo usado. O nome `qbasic` também está livre
no PyPI (verificado em novembro de 2026), caso um dia se queira que o nome de instalação
seja igual ao de importação. Trocar exigiria criar um projeto novo e avisar quem usa
`pip install Q-BASIC`.
