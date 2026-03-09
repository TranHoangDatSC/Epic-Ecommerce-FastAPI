-- reviews.sql
CREATE TABLE review (
    review_id SERIAL PRIMARY KEY,
    product_id INT NOT NULL,
    buyer_id INT NOT NULL,
    rating SMALLINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment VARCHAR(500),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_review_buyer_product UNIQUE (product_id, buyer_id),
    FOREIGN KEY (product_id) REFERENCES product(product_id),
    FOREIGN KEY (buyer_id) REFERENCES "user"(user_id)
);