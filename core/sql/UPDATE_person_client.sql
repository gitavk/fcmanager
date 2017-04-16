UPDATE person_client c
SET (first_name, last_name, patronymic
    , gender, born_date, avatar, address
    , phone, email, passport, note) 
    = (n.first_name, n.last_name, n.patronymic
    , n.gender, n.born_date, n.avatar, n.address
    , n.phone, n.email, n.passport, n.note) 
FROM (
SELECT id, first_name, last_name, patronymic
    , gender, born_date, avatar, address
    , phone, email, passport, note
FROM person_new 
) n
Where c.id=n.id;