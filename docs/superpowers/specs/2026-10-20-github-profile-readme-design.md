# Design: perfil GitHub de Nicolas Gabriel

## Objetivo

Criar o repositório especial público `nicolas-takimo/nicolas-takimo` para transformar a página do GitHub de Nicolas Gabriel em uma apresentação profissional bilíngue, visualmente marcante e fiel à sua atuação.

O perfil deve comunicar, em poucos segundos:

- formação em Engenharia da Computação;
- atuação como desenvolvedor full stack e CTO da FireTheBox;
- trabalho com Mobile, Web, IoT e AWS;
- experiência com React Native e Flutter no desenvolvimento mobile;
- capacidade de conectar software, dispositivos e infraestrutura em nuvem.

O estilo será inspirado no clima de “missão tecnológica” da referência enviada, mas usará composição, textos, órbitas, cores e hierarquia próprios.

## Público e critérios de sucesso

O público principal é formado por recrutadores, parceiros, clientes e outros desenvolvedores. O resultado será considerado bem-sucedido quando:

1. o README aparecer no topo de `github.com/nicolas-takimo`;
2. o posicionamento profissional puder ser entendido sem rolagem extensa;
3. o conteúdo estiver correto em português e inglês;
4. as métricas públicas forem atualizadas automaticamente;
5. todas as imagens funcionarem no tema escuro e continuarem legíveis em telas pequenas;
6. a automação puder falhar sem apagar ou quebrar os SVGs já publicados.

## Abordagem escolhida

Será usado um gerador próprio em Python, executado pelo GitHub Actions. Essa abordagem foi escolhida em vez de imagens totalmente estáticas ou cartões hospedados por terceiros porque oferece identidade própria, controle de disponibilidade e atualização automática.

O README será leve: texto Markdown/HTML e quatro SVGs versionados no próprio repositório. O gerador consultará apenas informações públicas do GitHub e produzirá novamente os SVGs quando houver alteração relevante.

## Estrutura do perfil

### Apresentação textual

O topo terá:

- nome: `Nicolas Gabriel`;
- título em inglês: `Computer Engineer · Full-Stack Developer`;
- subtítulo em português: `Engenheiro da Computação criando produtos conectados de ponta a ponta`;
- focos: `Mobile · Web · IoT · AWS`;
- vínculo profissional: `CTO @ FireTheBox`;
- localização ampla: `Mato Grosso, Brasil`;
- links apenas quando forem públicos e confirmados. Nesta primeira versão, o GitHub será o único link garantido; e-mail, LinkedIn e portfólio não serão inventados.

### SVG 1 — órbita tecnológica

O cabeçalho visual terá Nicolas no núcleo e quatro trilhas conectando Mobile, Web, IoT e AWS. Tecnologias secundárias aparecerão como pequenos nós: TypeScript, React, Next.js, Node.js, Python, React Native, Flutter, Firebase e RFID.

O gráfico será original, com fundo azul-marinho quase preto, ciano como cor principal, violeta para mobile, verde para cloud e âmbar para IoT. A arte não reproduzirá coordenadas, frases ou elementos exclusivos do perfil de referência.

### SVG 2 — telemetria pública

O painel exibirá somente números verificáveis e públicos:

- repositórios públicos próprios;
- contribuições públicas no ano corrente;
- seguidores;
- quantidade de linguagens detectadas nos repositórios públicos próprios.

Repositórios derivados por fork não entrarão nas contagens de linguagem. Valores indisponíveis serão mostrados como `—`, nunca como zero presumido.

### SVG 3 — mapa de stack

A stack será organizada por domínio, não como uma lista sem hierarquia:

- Mobile: React Native e Flutter;
- Web: TypeScript, React, Next.js e Node.js;
- IoT: RFID, integração de dispositivos e Firebase;
- Cloud: AWS;
- Supporting tools: Python e GitHub Actions.

As linguagens públicas poderão contribuir para a proporção visual, mas não removerão tecnologias declaradas pelo usuário que ainda não estejam representadas em repositórios públicos.

### SVG 4 — projetos em destaque

A primeira versão destacará:

1. `gavioes-style-fluxos` — interface e fluxos em React/TypeScript;
2. `graze` — aplicação web baseada em Next.js e contratos inteligentes;
3. `TCC-Controle-de-acesso-remoto-usando-Digiprox-S--202` — pesquisa aplicada em controle de acesso, RFID e Firebase.

Cada cartão terá título, descrição bilíngue curta, domínio principal e link no README. Se um projeto for removido ou ficar inacessível, o gerador manterá o cartão com texto curado e omitirá apenas métricas remotas indisponíveis.

## Arquitetura de arquivos

```text
README.md
config.yml
.github/workflows/generate-profile.yml
generator/
  __init__.py
  main.py
  github_client.py
  models.py
  svg.py
  templates/
    orbit_header.py
    telemetry.py
    stack_map.py
    featured_projects.py
assets/generated/
  orbit-header.svg
  telemetry.svg
  stack-map.svg
  featured-projects.svg
tests/
  test_config.py
  test_github_client.py
  test_svg_generation.py
requirements.txt
requirements-dev.txt
```

`config.yml` concentrará conteúdo editorial, tecnologias e projetos. A coleta remota ficará isolada em `github_client.py`; os templates receberão modelos já normalizados e não farão chamadas de rede. Assim, conteúdo, dados e renderização poderão ser testados separadamente.

## Fluxo de atualização

1. O workflow será executado manualmente, em cada alteração relevante e uma vez por dia.
2. O token padrão `GITHUB_TOKEN` consultará dados públicos pela API do GitHub.
3. O gerador validará e normalizará a resposta.
4. Os quatro SVGs serão escritos primeiro em uma pasta temporária.
5. Somente após todos serem gerados e validados eles substituirão os arquivos publicados.
6. O workflow fará commit apenas quando o conteúdo realmente mudar.

O workflow terá permissão mínima de `contents: write`. Nenhum Personal Access Token será armazenado. Falhas de rede encerrarão a execução sem alterar os SVGs existentes.

## Responsividade e acessibilidade

Os SVGs usarão `viewBox` e largura relativa para se adaptar ao README. Textos essenciais terão contraste alto e tamanho legível. Cada imagem terá texto alternativo descritivo no README. A informação não dependerá apenas de cor: domínios e métricas também terão rótulos explícitos.

Os textos serão curtos e bilíngues sem duplicar blocos inteiros. O inglês funcionará como linguagem principal dos títulos técnicos e o português dará contexto profissional.

## Tratamento de erros

- Resposta parcial da API: preservar conteúdo curado e usar `—` no dado remoto ausente.
- Limite de API: encerrar sem publicar arquivos parciais.
- Repositório destacado indisponível: preservar título e descrição configurados, removendo apenas a métrica remota.
- SVG inválido: falhar nos testes e não realizar commit automático.
- Nenhuma mudança de dados: concluir sem criar commit vazio.

## Verificação

Antes da publicação serão executados:

- testes unitários do carregamento de configuração e normalização da API;
- geração offline com fixtures para os quatro SVGs;
- validação XML de cada SVG;
- verificação de que o README referencia somente arquivos existentes;
- renderização visual em larguras desktop e mobile;
- execução manual do workflow após a criação do repositório;
- conferência final da página pública do perfil.

## Fora do escopo inicial

- expor contribuições, organizações ou repositórios privados;
- inventar anos de experiência, clientes ou métricas;
- publicar e-mail, LinkedIn ou portfólio não confirmados;
- criar site pessoal;
- copiar código, textos ou identidade visual do perfil usado como referência;
- usar serviços externos de cartões de estatísticas como dependência obrigatória.

## Entrega

A entrega termina quando o repositório público `nicolas-takimo/nicolas-takimo` estiver criado, o workflow tiver concluído com sucesso e o README estiver visível no perfil com os quatro painéis íntegros.
