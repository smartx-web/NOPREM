ALTER TABLE pus DROP CONSTRAINT IF EXISTS pus_lga_check;
ALTER TABLE pus ADD CONSTRAINT pus_lga_check CHECK(lga IN ('Ado','Agatu','Apa','Buruku','Gboko','Guma','Gwer East','Gwer West','Katsina-Ala','Konshisha','Kwande','Logo','Makurdi','Obi','Ogbadibo','Ohimini','Oju','Okpokwu','Otukpo','Tarka','Ukum','Ushongo','Vandeikya'));
INSERT INTO schema_migrations(version) VALUES(3) ON CONFLICT(version) DO NOTHING;
