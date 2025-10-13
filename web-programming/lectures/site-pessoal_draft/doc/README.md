# Website Retro-Futurista Interativo

## Visão Geral

Este projeto é um website de portfólio single-page application (SPA) com uma estética retro-futurista. Ele foi desenvolvido para ser dinâmico, acessível e performático, com um design que remete à computação clássica dos anos 80 e 90, mas com tecnologias web modernas.

## Estrutura do Projeto

O projeto segue uma arquitetura modular em JavaScript, separando as responsabilidades em diferentes componentes, como controladores, views e modelos. A seguir, uma descrição dos principais arquivos e diretórios:

-   `index.html`: O ponto de entrada da aplicação, contendo a estrutura HTML básica e os links para os arquivos CSS e JS.
-   `main.css`, `base.css`, `components.css`, `layout.css`, `variables.css`: Arquivos CSS que definem os estilos da aplicação, desde a base e tipografia até os componentes e layout responsivo.
-   `app.js`: O arquivo principal da aplicação, responsável por inicializar todos os módulos, controladores e views.
-   `/home/ubuntu/upload/controllers`: Contém os controladores que gerenciam a lógica da aplicação:
    -   `MainController.js`: O controlador principal que orquestra a inicialização e o carregamento de conteúdo.
    -   `NavigationController.js`: Gerencia a navegação, o scroll suave e o efeito de "flashback".
    -   `SectionController.js`: Controla a renderização e o conteúdo das seções dinâmicas.
-   `/home/ubuntu/upload/views`: Contém as views que cuidam da apresentação e da interface do usuário:
    -   `SectionView.js`: Responsável por renderizar as seções de conteúdo, como cartões, timelines e galerias.
    -   `NavigationView.js`, `HeroView.js`, `FooterView.js`: Views para a navegação, a seção de destaque e o rodapé.
-   `/home/ubuntu/upload/models`: Contém os modelos de dados:
    -   `ContentModel.js`: Fornece o conteúdo para as seções do website.
-   `/home/ubuntu/upload/managers`: Contém os gerenciadores de funcionalidades específicas:
    -   `ViewManager.js`: Gerencia a renderização e o cache de views.
    -   `ThemeManager.js`: Controla a troca de temas (claro/escuro).
    -   `AccessibilityManager.js`: Melhora a acessibilidade do site.
    -   `PerformanceMonitor.js`: Monitora o desempenho da aplicação.

## Como Executar

Para executar o projeto, basta abrir o arquivo `index.html` em um navegador web moderno. Não é necessário um servidor local, pois o projeto é totalmente baseado em arquivos estáticos.

## Funcionalidades Implementadas

-   **Carregamento Dinâmico de Conteúdo**: O conteúdo das seções é carregado dinamicamente a partir do `ContentModel.js`, permitindo fácil atualização e manutenção.
-   **Design Retro-Futurista**: Foram adicionadas fontes de estilo retro (`VT323`, `Press Start 2P`) e um efeito de brilho neon para ícones, criando uma estética única.
-   **Navegação com "Flashback"**: Ao navegar entre as seções, um efeito de "flashback" com um filtro CRT é aplicado, proporcionando uma transição visual interessante.
-   **Responsividade**: O layout se adapta a diferentes tamanhos de tela, desde dispositivos móveis até desktops, garantindo uma boa experiência de usuário em qualquer dispositivo.
-   **Acessibilidade**: O site foi desenvolvido com foco em acessibilidade, incluindo suporte a leitores de tela, navegação por teclado e atributos ARIA.
-   **Otimização de Desempenho**: O `PerformanceMonitor.js` monitora o desempenho da aplicação, e o lazy loading de imagens garante um carregamento rápido da página.

