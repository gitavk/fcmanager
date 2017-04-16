DROP VIEW v_issuance_goods;

CREATE OR REPLACE VIEW v_issuance_goods 
(id, balance, market_id
, goods_id, expirydate) 
AS
(
SELECT issg.id, issg.balance, iss.market_id
	, invg.goods_id, invg.expirydate
FROM finance_issuancegoods issg
     LEFT JOIN finance_issuance iss
     ON issg.issuance_id = iss.id
     LEFT JOIN finance_invoicegoods invg
     ON issg.goods_id = invg.id
WHERE issg.balance > 0
);

DROP VIEW v_issuance_goods_recovery;

CREATE OR REPLACE VIEW v_issuance_goods_recovery
(id, balance, count
, market_id
, goods_id, expirydate) 
AS
(
SELECT issg.id, issg.balance, issg.count
	, iss.market_id
	, invg.goods_id, invg.expirydate
FROM finance_issuancegoods issg
     LEFT JOIN finance_issuance iss
     ON issg.issuance_id = iss.id
     LEFT JOIN finance_invoicegoods invg
     ON issg.goods_id = invg.id
WHERE issg.balance < issg.count
);