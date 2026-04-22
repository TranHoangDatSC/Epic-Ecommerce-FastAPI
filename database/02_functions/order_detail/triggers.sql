-- =
-- ORDER DETAIL TRIGGERS
-- ===========================================================================
-- Triggers for order processing and business rules enforcement
-- ===========================================================================

-- Trigger function to prevent self-buying
-- Business Rule: Sellers cannot buy their own products
CREATE OR REPLACE FUNCTION check_no_self_buying()
RETURNS TRIGGER AS $$
DECLARE
    order_buyer_id INT;
    product_seller_id INT;
BEGIN
    SELECT buyer_id INTO order_buyer_id
    FROM "order"
    WHERE order_id = NEW.order_id;

    SELECT seller_id INTO product_seller_id
    FROM product
    WHERE product_id = NEW.product_id;

    IF order_buyer_id IS NULL OR product_seller_id IS NULL THEN
        RAISE EXCEPTION 'INVALID_ORDER_OR_PRODUCT: Invalid order or product reference';
    END IF;

    IF order_buyer_id = product_seller_id THEN
        PERFORM log_system_action(
            order_buyer_id,
            'SELF_BUY_BLOCKED',
            'order_detail',
            NEW.order_detail_id,
            'Attempted to buy own product (product_id: ' || NEW.product_id || ')'
        );
        RAISE EXCEPTION 'BUSINESS_RULE_VIOLATION: Sellers cannot buy their own products.';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public;

CREATE TRIGGER trg_no_self_buying
BEFORE INSERT ON order_detail
FOR EACH ROW EXECUTE FUNCTION check_no_self_buying();

-- Trigger function to update stock and handle inventory management
-- Automatically reduces product quantity when order is placed
CREATE OR REPLACE FUNCTION update_stock_on_order()
RETURNS TRIGGER AS $$
DECLARE
    current_quantity INT;
    order_buyer_id INT;
BEGIN
    SELECT quantity INTO current_quantity
    FROM product
    WHERE product_id = NEW.product_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'PRODUCT_NOT_FOUND: Product does not exist';
    END IF;

    IF current_quantity < NEW.quantity THEN
        RAISE EXCEPTION 'INSUFFICIENT_STOCK: Only % items available, requested %',
                       current_quantity, NEW.quantity;
    END IF;

    SELECT buyer_id INTO order_buyer_id
    FROM "order"
    WHERE order_id = NEW.order_id;

    UPDATE product
    SET quantity = quantity - NEW.quantity,
        updated_at = CURRENT_TIMESTAMP
    WHERE product_id = NEW.product_id;

    PERFORM log_system_action(
        order_buyer_id,
        'STOCK_DECREASE',
        'product',
        NEW.product_id,
        'Stock decreased by ' || NEW.quantity || ' for order ' || NEW.order_id ||
        ' (remaining: ' || (current_quantity - NEW.quantity) || ')'
    );

    RETURN NEW;
END;
$$ LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public;

-- CREATE TRIGGER trg_update_stock
-- BEFORE INSERT ON order_detail
-- FOR EACH ROW EXECUTE FUNCTION update_stock_on_order();

-- -- Trigger function to validate order details before insertion
-- CREATE OR REPLACE FUNCTION validate_order_detail()
-- RETURNS TRIGGER AS $$
-- DECLARE
--     product_status SMALLINT;
-- BEGIN
--     SELECT status INTO product_status
--     FROM product
--     WHERE product_id = NEW.product_id;

--     IF NOT FOUND THEN
--         RAISE EXCEPTION 'INVALID_PRODUCT: Product does not exist';
--     END IF;

--     IF product_status != 1 THEN
--         RAISE EXCEPTION 'PRODUCT_NOT_AVAILABLE: Product is not available for purchase (status: %)',
--                        get_product_status_text(product_status);
--     END IF;

--     IF NEW.quantity <= 0 THEN
--         RAISE EXCEPTION 'INVALID_QUANTITY: Quantity must be greater than 0';
--     END IF;

--     IF NEW.price_at_purchase <= 0 THEN
--         RAISE EXCEPTION 'INVALID_PRICE: Price must be greater than 0';
--     END IF;

--     NEW.subtotal := NEW.price_at_purchase * NEW.quantity;

--     RETURN NEW;
-- END;
$$ LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public;

CREATE TRIGGER trg_validate_order_detail
BEFORE INSERT ON order_detail
FOR EACH ROW EXECUTE FUNCTION validate_order_detail();

-- Trigger function to update voucher usage when applied to orders
CREATE OR REPLACE FUNCTION update_voucher_usage()
RETURNS TRIGGER AS $$
DECLARE
    voucher_code VARCHAR(50);
    order_buyer_id INT;
BEGIN
    IF NEW.voucher_id IS NOT NULL THEN
        SELECT code, buyer_id INTO voucher_code, order_buyer_id
        FROM voucher
        JOIN "order" ON "order".voucher_id = voucher.voucher_id
        WHERE "order".order_id = NEW.order_id;

        UPDATE voucher
        SET usage_count = usage_count + 1
        WHERE voucher_id = NEW.voucher_id;

        PERFORM log_system_action(
            order_buyer_id,
            'VOUCHER_USED',
            'order',
            NEW.order_id,
            'Voucher ' || voucher_code || ' applied to order'
        );
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public;

CREATE TRIGGER trg_update_voucher_usage
AFTER INSERT ON "order"
FOR EACH ROW
WHEN (NEW.voucher_id IS NOT NULL)
EXECUTE FUNCTION update_voucher_usage();
