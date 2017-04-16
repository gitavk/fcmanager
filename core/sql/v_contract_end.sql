DROP VIEW v_contract_end;

CREATE OR REPLACE VIEW v_contract_end 
(id, client_id, contract_type_id
, date, date_joined, number
,date_start, date_end, date_finish, manager_id) AS
(
SELECT c.id, c.client_id, c.contract_type_id
	, c.date, c.date_joined, c.number
	, c.date_start, c.date_end
	, c.date_end - 1 as date_finish
	, p.manager_id
FROM contract_contract c
-- client manager
	LEFT JOIN person_client p
		ON c.client_id = p.id
);