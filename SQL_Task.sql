/*SELECT ALL AND RUN WILL REPLICATE THE RESULT*/

/*prep*/
DROP TABLE IF EXISTS SQL_TASK;
CREATE TEMPORARY TABLE IF NOT EXISTS SQL_TASK AS (
    WITH ORDERS (ID, NUMBER, COUNTRY, CUSTOMER_ID) AS
        (
            VALUES (1, 'O-01', 'DE', 1)
                 , (4, 'O-02', 'AT', 2)
                 , (5, 'O-03', 'DE', 2)
                 , (6, 'O-05', 'AT', 2)
                 , (8, 'O-06', 'DE', 3)
                 , (10, 'O-10', 'DE', 3)
                 , (11, 'O-11', 'AT', 3)
                 , (12, 'O-123', 'DE', 1)
        )
       , CUSTOMERS (ID, COUNTRY, NAME)             AS
        (
            VALUES (1, 'DE', 'John Doe')
                 , (2, 'AT', 'John Snow')
                 , (3, 'DE', 'Johnny B. Goode')
        )
    SELECT O.ID      AS ORDER_ID
         , O.NUMBER  AS ORDER_NUMBER
         , O.COUNTRY AS ORDER_COUNTRY
         , C.ID      AS CUSTOMER_ID
         , C.COUNTRY AS CUSTOMER_COUNTRY
         , C.NAME    AS CUSTOMER_NAME
    FROM ORDERS AS O
             INNER JOIN CUSTOMERS AS C ON C.ID = O.CUSTOMER_ID);
/*prep*/

/*1. Select Customer Name and orders in his/her home country + not in the home*/
SELECT CUSTOMER_NAME,
       COUNT(*) FILTER ( WHERE CUSTOMER_COUNTRY = ORDER_COUNTRY )  AS SAME,     -- only for postgres (else use case)
       COUNT(*) FILTER ( WHERE CUSTOMER_COUNTRY != ORDER_COUNTRY ) AS DIFFERENT -- only for postgres (else use case)
FROM SQL_TASK
GROUP BY 1;


/*2. Find the gaps in orders ids, i.e. missing id values in the sequence*/
WITH GET_LEAD AS (SELECT ORDER_ID,
                         LEAD(ORDER_ID) OVER (ORDER BY ORDER_ID) AS NEXT_NUM
                  FROM SQL_TASK)
SELECT ORDER_ID + 1 AS START,
       NEXT_NUM - 1 AS "END"
FROM GET_LEAD
WHERE ORDER_ID + 1 <> NEXT_NUM;


/*3. Find gaps in orders numbers, i.e. missing number in the sequence*/
WITH GET_LEAD AS (SELECT SPLIT_PART(ORDER_NUMBER, '-', 2)::NUMERIC                 AS ORDER_NUMBER,
                         LEAD(SPLIT_PART(ORDER_NUMBER, '-', 2))
                         OVER (ORDER BY SPLIT_PART(ORDER_NUMBER, '-', 2))::NUMERIC AS NEXT_NUM
                  FROM SQL_TASK)
SELECT ORDER_NUMBER + 1 AS START,
       NEXT_NUM - 1     AS "END"
FROM GET_LEAD
WHERE ORDER_NUMBER + 1 <> NEXT_NUM;
