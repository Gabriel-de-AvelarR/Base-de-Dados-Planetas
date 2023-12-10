--Objetivo: buscar planetas que tenham um elemento quimico especifico
--saida: planeta e fonte de origem

-- Primeira parte: Espécies encontradas no planeta com o elemento químico Ni
SELECT
    EQ.SIGLA AS ELEMENTO_QUIMICO,    -- Seleciona o símbolo do elemento químico
    P.NOME AS PLANETA,               -- Seleciona o nome do planeta
    'Espécie: ' || E.NOME AS ENCONTRADO_EM  -- Concatena 'Espécie: ' com o nome da espécie
FROM
    ELEMENTO_QUIMICO EQ              -- Tabela de elementos químicos
LEFT JOIN ESPECIES E ON EQ.SIGLA = E.ELEMENTO  -- Junção com a tabela de espécies
LEFT JOIN AMBIENTE A ON E.NOMEPLANETA = A.PLANETA  -- Junção com a tabela de ambientes
LEFT JOIN PLANETA P ON A.PLANETA = P.NOME  -- Junção com a tabela de planetas
WHERE
    EQ.SIGLA = 'Ni'  -- Restrição para o elemento químico Ni

-- União entre as duas partes usando UNION
UNION

-- Segunda parte: Minérios do tipo Ni encontrados em algum planeta
SELECT
    EQ.SIGLA AS ELEMENTO_QUIMICO,    -- Seleciona o símbolo do elemento químico
    P.NOME AS PLANETA,               -- Seleciona o nome do planeta
    'Minério: ' || M.NOME AS ENCONTRADO_EM  -- Concatena 'Minério: ' com o nome do minério
FROM
    ELEMENTO_QUIMICO EQ              -- Tabela de elementos químicos
LEFT JOIN MINERIO M ON EQ.SIGLA = M.ELEMENTO  -- Junção com a tabela de minérios
LEFT JOIN POSSUI POS ON M.NOME = POS.MINERIO  -- Junção com a tabela de posses de minérios
LEFT JOIN AMBIENTE A ON POS.AMBIENTE = A.PLANETA  -- Junção com a tabela de ambientes
LEFT JOIN PLANETA P ON A.PLANETA = P.NOME  -- Junção com a tabela de planetas
WHERE
    EQ.SIGLA = 'Ni';  -- Restrição para o elemento químico Ni



---------------------------------------------------------------------------------------------
--Objetivo: Encontrar os vendedores que mais lucraram em um único dia (maior valor total vendido em um dia):
-- Execucao: Seleciona o nome do vendedor (V.NOME) e a soma do lucro total para cada vendedor

SELECT
    V.NOME,  -- Seleciona o nome do vendedor
    SUM(VF.QUANTIDADE * F.DURABILIDADE) AS LUCRO_TOTAL  -- Calcula e soma o lucro total para cada vendedor
FROM
    VENDE_FABRICAVEL VF  -- Tabela de vendas de fabricáveis
JOIN FABRICAVEIS F ON VF.FABRICAVEL = F.NOME  -- Junção com a tabela de fabricáveis
JOIN VENDEDOR V ON VF.VENDEDOR = V.NOME  -- Junção com a tabela de vendedores
GROUP BY
    V.NOME, VF."DATA"  -- Agrupa os resultados pelo nome do vendedor e a data de venda
ORDER BY
    LUCRO_TOTAL DESC  -- Ordena os resultados pelo lucro total em ordem decrescente
FETCH FIRST ROW ONLY;  -- Limita o resultado a apenas a primeira linha (maior lucro total)


----------------------------------------------------------------------------------
--Objetivo: Dado um fabricavel, selecionar os 5 fabricaveis mais proximos dele em distancia
-- Execucao: Consulta para encontrar os 5 fabricáveis mais próximos da 'Lunar Base'

-- Seleciona o nome do fabricável (F.NOME), as posições X e Y do local (L.POSICAOX, L.POSICAOY),
-- e calcula a distância euclidiana até as coordenadas (5, 8).
SELECT
    F.NOME AS FABRICAVEL,  -- Seleciona o nome do fabricável
    L.POSICAOX,  -- Seleciona a posição X do local
    L.POSICAOY,  -- Seleciona a posição Y do local
    TRUNC(SQRT(POWER(5 - L.POSICAOX, 2) + POWER(8 - L.POSICAOY, 2))) AS DISTANCIA  -- Calcula a distância euclidiana
FROM
    FABRICAVEIS F  -- Tabela de fabricáveis
JOIN "LOCAL" L ON F.NOME = L.FABRICAVEL  -- Junção com a tabela de locais usando o nome do fabricável
WHERE
    F.NOME <> 'Space Station'  -- Restrição para excluir 'Space Station'
ORDER BY
    DISTANCIA  -- Ordena os resultados pela distância euclidiana
FETCH FIRST 5 ROWS ONLY;  -- Limita o resultado às primeiras 5 linhas



-----------------------------------------------------------------------------------
--Objetivo: Distancia total viajada por cada astronauta ordenados por quem viajou mais

-- Execucao: Seleciona o nome do astronauta (V.ASTRONAUTA) e a soma total da distância percorrida para cada astronauta.
SELECT
    V.ASTRONAUTA,  -- Seleciona o nome do astronauta
    SUM(R.DISTANCIA_TOTAL) AS DISTANCIA_TOTAL  -- Calcula e soma a distância total percorrida por cada astronauta
FROM
    VIAGEM V  -- Tabela de viagens
JOIN ROTA R ON V.ORIGEM = R.ORIGEM AND V.DESTINO = R.DESTINO  -- Junção com a tabela de rotas usando origem e destino
GROUP BY
    V.ASTRONAUTA  -- Agrupa os resultados pelo nome do astronauta
ORDER BY
    DISTANCIA_TOTAL DESC;  -- Ordena os resultados pela distância total em ordem decrescente


------------------------------------------------------------------------------------
--Objetivo: identificar a espécie e o minerio mais comum em um bioma
-- CTE que calcula os minerais mais comuns em cada bioma
WITH MostCommonMineralInBiome AS (
  SELECT
    A.BIOMA,                           -- Bioma em análise
    M.TIPO AS TIPO_DE_MINERIO,         -- Tipo do mineral
    M.NOME AS MINERIO_MAIS_COMUM,      -- Nome do mineral mais comum
    COUNT(*) AS QTD,                   -- Contagem de ocorrências do mineral
    ROW_NUMBER() OVER (PARTITION BY A.BIOMA ORDER BY COUNT(*) DESC) AS RN  -- Número de linha baseado na contagem decrescente
  FROM
    AMBIENTE A
  JOIN
    POSSUI P ON A.PLANETA = P.AMBIENTE  -- Junção com a tabela de posses usando o planeta
  JOIN
    MINERIO M ON P.MINERIO = M.NOME  -- Junção com a tabela de minérios usando o nome do mineral
  GROUP BY
    A.BIOMA, M.TIPO, M.NOME
),
-- CTE que calcula as espécies mais comuns em cada bioma
MostCommonSpeciesInBiome AS (
  SELECT
    A.BIOMA,                           -- Bioma em análise
    E.TIPO AS TIPO_DE_ESPECIE,         -- Tipo da espécie
    E.NOME AS ESPECIE_MAIS_COMUM,      -- Nome da espécie mais comum
    COUNT(*) AS QTD,                   -- Contagem de ocorrências da espécie
    ROW_NUMBER() OVER (PARTITION BY A.BIOMA ORDER BY COUNT(*) DESC) AS RN  -- Número de linha baseado na contagem decrescente
  FROM
    AMBIENTE A
  JOIN
    ESPECIES E ON A.PLANETA = E.NOMEPLANETA  -- Junção com a tabela de espécies usando o nome do planeta
  GROUP BY
    A.BIOMA, E.TIPO, E.NOME
)
-- Seleciona informações sobre os minerais e espécies mais comuns em cada bioma
SELECT
  A.BIOMA,                                  -- Bioma em análise
  M.TIPO_DE_MINERIO AS MINERIO_MAIS_COMUM,  -- Tipo do mineral mais comum
  M.MINERIO_MAIS_COMUM AS NOME_DO_MINERIO_MAIS_COMUM,  -- Nome do mineral mais comum
  S.TIPO_DE_ESPECIE AS ESPECIE_MAIS_COMUM,  -- Tipo da espécie mais comum
  S.ESPECIE_MAIS_COMUM AS NOME_DA_ESPECIE_MAIS_COMUM  -- Nome da espécie mais comum
FROM
  (SELECT DISTINCT BIOMA FROM AMBIENTE) A  -- Subconsulta para obter biomas distintos
LEFT JOIN
  MostCommonMineralInBiome M ON A.BIOMA = M.BIOMA AND M.RN = 1  -- Junção com CTE de minerais mais comuns usando o bioma
LEFT JOIN
  MostCommonSpeciesInBiome S ON A.BIOMA = S.BIOMA AND S.RN = 1  -- Junção com CTE de espécies mais comuns usando o bioma;


-------------------------------------------------------------------------
--Dado um ano, retornar TODOS os planetas visitados por um astronauta

