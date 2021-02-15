CREATE TABLE card (
    id INT NOT NULL AUTO_INCREMENT,
    title VARCHAR(255),
    type BLOB,
    assign BLOB,
    goal BLOB,
    PRIMARY KEY(id)
);
CREATE TABLE entry (
    id INT NOT NULL AUTO_INCREMENT,
    timeframe BLOB,
    columns BLOB,
    progress BLOB,
    takeaways BLOB,
    plans BLOB,
    card_id INT NOT NULL,
    PRIMARY KEY(id),
    FOREIGN KEY(card_id) REFERENCES card(id)
);
