CREATE TABLE geometry_columns (
f_table_name VARCHAR(256) NOT NULL,
f_geometry_column VARCHAR(256) NOT NULL,
type VARCHAR(30) NOT NULL,
coord_dimension INTEGER NOT NULL,
srid INTEGER,
spatial_index_enabled INTEGER NOT NULL);
CREATE TABLE spatial_ref_sys (
srid INTEGER NOT NULL PRIMARY KEY,
auth_name VARCHAR(256) NOT NULL,
auth_srid INTEGER NOT NULL,
ref_sys_name VARCHAR(256),
proj4text VARCHAR(2048) NOT NULL);
CREATE VIEW geom_cols_ref_sys AS
SELECT  f_table_name, f_geometry_column, type,
coord_dimension, spatial_ref_sys.srid AS srid,
auth_name, auth_srid, ref_sys_name, proj4text
FROM geometry_columns, spatial_ref_sys
WHERE geometry_columns.srid = spatial_ref_sys.srid;
CREATE TRIGGER fkd_refsys_geocols BEFORE DELETE ON spatial_ref_sys
FOR EACH ROW BEGIN
SELECT RAISE(ROLLBACK, 'delete on table ''spatial_ref_sys'' violates constraint: ''geometry_columns.srid''')
WHERE (SELECT srid FROM geometry_columns WHERE srid = OLD.srid) IS NOT NULL;
END;
CREATE TRIGGER fki_geocols_refsys BEFORE INSERT ON geometry_columns
FOR EACH ROW BEGIN
SELECT RAISE(ROLLBACK, 'insert on table ''geometry_columns'' violates constraint: ''spatial_ref_sys.srid''')
WHERE  NEW."srid" IS NOT NULL
AND (SELECT srid FROM spatial_ref_sys WHERE srid = NEW.srid) IS NULL;
END;
CREATE TRIGGER fku_geocols_refsys BEFORE UPDATE ON geometry_columns
FOR EACH ROW BEGIN
SELECT RAISE(ROLLBACK, 'update on table ''geometry_columns'' violates constraint: ''spatial_ref_sys.srid''')
WHERE  NEW.srid IS NOT NULL
AND (SELECT srid FROM spatial_ref_sys WHERE srid = NEW.srid) IS NULL;
END;
CREATE UNIQUE INDEX idx_geocols ON geometry_columns
(f_table_name, f_geometry_column);
