.open sql.db;

CREATE TABLE IF NOT EXISTS organization (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS contact (
    id INTEGER PRIMARY KEY,
    first_name VARCHAR(31) NOT NULL,
    last_name VARCHAR(31) NOT NULL,
    dob CHAR(10) NOT NULL,
    organization_id INTEGER NOT NULL,
    FOREIGN KEY (organization_id) 
        REFERENCES organization(id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS contact_info (
    id INTEGER PRIMARY KEY,
    cat INTEGER NOT NULL,
    label VARCHAR(255) NOT NULL,
    info VARCHAR(255) NOT NULL,
    contact_id INTEGER NOT NULL,
    FOREIGN KEY (contact_id) 
        REFERENCES contact(id)
        ON DELETE CASCADE
);



