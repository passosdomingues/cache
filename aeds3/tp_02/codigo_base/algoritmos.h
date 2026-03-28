#ifndef ALGORITMOS_H
#define ALGORITMOS_H

/* --- Funções Principais (Exigidas pelo base.c) --- */
long int programacao_dinamica(char *s1, char *s2);
long int guloso(char *s1, char *s2);

/*******************************************************
Caso necessário, este arquivo também pode ser modificado
*******************************************************/

/* --- Nossas Funções Auxiliares --- */
long int calcular_score(char a, char b);
long int max3(long int a, long int b, long int c);

#endif // ALGORITMOS_H

