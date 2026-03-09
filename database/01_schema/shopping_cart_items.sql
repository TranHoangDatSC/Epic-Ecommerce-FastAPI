-- shopping_cart_items.sql
CREATE TABLE shopping_cart_item (
    item_id SERIAL PRIMARY KEY,
    cart_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    added_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cart_id) REFERENCES shopping_cart(cart_id),
    FOREIGN KEY (product_id) REFERENCES product(product_id)
);