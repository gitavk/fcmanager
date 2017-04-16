DROP VIEW v_manager_sells;

CREATE OR REPLACE VIEW v_manager_sells 
(id, date, amount, goods_id
, contract_id, client_id
, selltype, manager_id, firstptt ) AS 
(
SELECT ch.id, ch.date, ch.amount, ch.goods_id
    , ch.contract_id, ch.client_id
    , CASE  WHEN ch.contract_id IS NOT NULL THEN 1
            WHEN ptt.id IS NOT NULL THEN 2
    ELSE 0
    END AS selltype
    , CASE  WHEN ch.contract_id IS NOT NULL THEN c.manager_id
    ELSE p.manager_id
    END AS manager_id
    , CASE  WHEN ch.contract_id IS NOT NULL THEN 1
            WHEN fptt.id IS NOT NULL THEN 1
    ELSE 0
    END AS firstptt
FROM finance_creditshistory ch
-- ptt name
    LEFT JOIN (SELECT g.id, g.name
                FROM finance_goods g
                    INNER JOIN finance_goodstype t
                        ON g.goods_type_id = t.id
                WHERE t.name = 'PTT'
                ) ptt
        ON ptt.id = ch.goods_id
-- contract manager
    LEFT JOIN contract_contract c
        ON c.id = ch.contract_id
-- ptt manager
    LEFT JOIN person_client p
        ON ch.client_id = p.id
-- first ptt
    LEFT JOIN (SELECT min(fch.id) as id, client_id, g.goods_type_id
                FROM finance_creditshistory fch
                    LEFT JOIN finance_goods g
                        ON g.id = fch.goods_id
                    INNER JOIN finance_goodstype t
                        ON g.goods_type_id = t.id
                    WHERE t.name = 'PTT'
                GROUP BY client_id, g.goods_type_id) fptt
        ON fptt.id = ch.id);