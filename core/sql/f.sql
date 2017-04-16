CREATE OR REPLACE FUNCTION type_active(int) 
RETURNS integer AS $$
DECLARE
    rec contract_contracttype%rowtype;
Begin
	<<typeforupdate>>
    FOR rec IN (select * from contract_contracttype Where date_start = current_date)
    LOOP
    	Update contract_contracttype
    	Set is_active = False
    	Where name = rec.name;
    	Update contract_contracttype 
    	Set is_active = True
    	Where id = rec.id;
	END LOOP typeforupdate;
	RETURN 1;
END;
$$ LANGUAGE plpgsql;