% ========================================= %
% lessonplan.cls - Classe LaTeX Personalizada para Planos de Aula
%
% Adaptado por: Rafael Passos Domingues
%   Com base no template de Eliza Diggins
%   e nos Documentos Técnicos do Modelo Pedagógico Senac
% ========================================= %
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{lessonplan}

% Permitir passar opções básicas como 12pt
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions\relax

% Classe base
\LoadClass[12pt]{article}

% Pacotes essenciais
\usepackage[
  left=0.25in,
  right=0.25in,
  top=0.7in,
  bottom=0.25in
]{geometry}
\usepackage[brazil]{babel}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{graphicx}
\usepackage{array}
\usepackage{fancyhdr}
\usepackage{hyperref}
\usepackage{booktabs}
\usepackage{xcolor}
\usepackage{float}

% Configuração de hiperlinks
\hypersetup{
    colorlinks=true,
    linkcolor=blue,
    filecolor=magenta,      
    urlcolor=cyan,
    pdftitle={Plano de Aula Senac},
    pdfauthor={Modelo Pedagógico Senac},
    pdfsubject={Educação Profissional}
}

% Variáveis definidas pelo usuário (inicialmente vazias)
\newcommand{\Institution}{}
\newcommand{\CourseTitle}{}
\newcommand{\LectureNumber}{}
\newcommand{\InstructorName}{}
\newcommand{\TopicArea}{}
\newcommand{\TeachingDate}{}
\newcommand{\TimeAllotted}{}
\newcommand{\CourseLevel}{}
\newcommand{\DeliveryMode}{}
\newcommand{\Materials}{}
\newcommand{\Competencia}{} % Nova variável: Competência
\newcommand{\MarcasFormativas}{} % Nova variável: Marcas Formativas
\newcommand{\UnidadeCurricular}{} % Nova variável: Unidade Curricular

% Estilo da página
\pagestyle{fancy}
\fancyhf{}
\lhead{\includegraphics[height=0.8cm]{logo_senac.png}} % Ajuste o caminho da logo
\rhead{\textbf{Plano de Aula}}
\lfoot{\Institution}
\rfoot{Página \thepage}
\renewcommand{\headrulewidth}{0.4pt}
\renewcommand{\footrulewidth}{0.4pt}

% Comando para imprimir o cabeçalho da aula
\newcommand{\PrintLessonHeader}{
  \begin{center}
    {\LARGE \textbf{Plano de Aula - Modelo Pedagógico Senac}} \\[1ex]
    {\large \textbf{Educação Profissional Baseada em Competências}} \\[2ex]
    \rule{\textwidth}{0.5pt}
  \end{center}
}

% Comando para imprimir a tabela de resumo com elementos do Modelo Senac
\newcommand{\PrintSummaryTable}{
  \vspace{-1ex}
  \noindent
  \begin{center}
  \begin{tabular}{@{} >{\bfseries}p{4cm} p{10cm} @{}}
    \toprule
    \textbf{Curso:} & \CourseTitle \\[1ex]
    \textbf{Aula Nº:} & \LectureNumber \\[1ex]
    \textbf{Unidade Curricular:} & \UnidadeCurricular \\[1ex]
    \textbf{Competência:} & \Competencia \\[1ex]
    \textbf{Marcas Formativas:} & \MarcasFormativas \\[1ex]
    \textbf{Instrutor:} & \InstructorName \\[1ex]
    \textbf{Área Temática:} & \TopicArea \\[1ex]
    \textbf{Data:} & \TeachingDate \\[1ex]
    \textbf{Duração:} & \TimeAllotted \\[1ex]
    \textbf{Nível do Curso:} & \CourseLevel \\[1ex]
    \textbf{Modalidade:} & \DeliveryMode \\[1ex]
    \textbf{Materiais:} & \Materials \\
    \bottomrule
  \end{tabular}
  \end{center}
  \vspace{0.5cm}
}

% Comando para criar uma tabela de objetivos de aprendizagem (estilo Senac)
\newenvironment{ObjetivosAprendizagem}{
  \section*{Objetivos da Aula}
  \textit{Esta seção descreve os principais objetivos de aprendizagem que os alunos devem alcançar ao final da aula, alinhados ao desenvolvimento da competência. Cada objetivo está escrito na perspectiva do aluno e relacionado aos elementos da competência.}
  \vspace{0.5cm}
  \renewcommand{\arraystretch}{1.5}
  \begin{center}
  \begin{tabular}{|p{9cm}|p{6cm}|}
  \hline
  \textbf{Objetivo da Aula (O que o aluno será capaz de fazer?)} & \textbf{Elementos Mobilizados} \\
  \hline
}{
  \hline
  \end{tabular}
  \end{center}
}

% Comando para criar uma tabela de componentes da aula (estilo Senac)
\newenvironment{ComponentesAula}{
  \section*{Componentes da Aula}
  \textit{Cada componente representa uma parte distinta da sequência instrucional, organizada conforme o ciclo ação-reflexão-ação.}
  \vspace{0.5cm}
  \renewcommand{\arraystretch}{1.8}
  \setlength{\tabcolsep}{6pt}
  \begin{center}
  \begin{tabular}{|c|p{7cm}|c|c|c|}
  \hline
  \textbf{\#} & \textbf{Descrição} & \textbf{Tempo} & \textbf{Recursos} & \textbf{Avaliação} \\
  \hline
  \hline
}{
  \hline
  \end{tabular}
  \end{center}
}

% Comando para criar um box de destaque para o ciclo ação-reflexão-ação
\newcommand{\CicloARA}[3]{
  \begin{center}
  \fbox{
    \begin{minipage}{0.9\textwidth}
      \textbf{Ciclo Ação-Reflexão-Ação:}
      \begin{enumerate}
        \item \textbf{Ação Inicial:} #1
        \item \textbf{Reflexão:} #2
        \item \textbf{Ação Qualificada:} #3
      \end{enumerate}
    \end{minipage}
  }
  \end{center}
}

% Comando para criar uma tabela de elementos da competência
\newcommand{\ElementosCompetencia}[3]{
  \section*{Elementos da Competência}
  \textit{Conforme definição do Modelo Pedagógico Senac, os elementos são mobilizados de forma articulada para o desenvolvimento da competência.}
  \vspace{0.5cm}
  \begin{center}
  \begin{tabular}{|p{3cm}|p{12cm}|}
  \hline
  \textbf{Conhecimentos} & #1 \\
  \hline
  \textbf{Habilidades} & #2 \\
  \hline
  \textbf{Atitudes/Valores} & #3 \\
  \hline
  \end{tabular}
  \end{center}
}

% Comando para criar uma tabela de indicadores da competência
\newenvironment{IndicadoresCompetencia}{
  \section*{Indicadores da Competência}
  \textit{Parâmetros essenciais que ajudam a identificar as principais etapas no desenvolvimento da competência. O atendimento a todos os indicadores é necessário para o desenvolvimento da competência.}
  \vspace{0.5cm}
  \begin{center}
  \begin{tabular}{|p{12cm}|c|}
  \hline
  \textbf{Indicador} & \textbf{Atendimento} \\
  \hline
}{
  \hline
  \end{tabular}
  \end{center}
  \vspace{0.5cm}
  \textit{Legenda: A (Atendido) | PA (Parcialmente Atendido) | NA (Não Atendido)}
}

% Configurações adicionais para o documento
\setlength{\parindent}{0pt}
\setlength{\parskip}{0.5em}

% Redefinição da seção para o estilo Senac
\renewcommand{\section}{\@startsection{section}{1}{0pt}%
  {-1ex plus -.5ex minus -.2ex}%
  {0.5ex plus .2ex}%
  {\normalfont\large\bfseries}}

% Redefinição da subseção
\renewcommand{\subsection}{\@startsection{subsection}{2}{0pt}%
  {-0.8ex plus -.5ex minus -.2ex}%
  {0.4ex plus .2ex}%
  {\normalfont\normalsize\bfseries}}