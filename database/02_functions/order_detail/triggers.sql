-- ==============================================================================
-- ORDER DETAIL TRIGGERS
-- ==============================================================================
-- Triggers for order processing and business rules enforcement
-- ==============================================================================

-- Trigger function to prevent self-buying
-- Business Rule: Sellers cannot buy their own products
CREATE OR REPLACE FUNCTION check_no_self_buying()
RETURNS TRIGGER AS $$
DECLARE
    order_buyer_id INT;
BEGIN
    -- Get buyer ID from the order
    SELECT buyer_id INTO order_buyer_id
    FROM "order"
    WHERE order_id = NEW.order_id;

    -- Check if buyer is the same as seller
    IF order_buyer_id = NEW.seller_id THEN
        -- Log the violation attempt
        PERFORM log_system_action(
            order_buyer_id,
            'SELF_BUY_BLOCKED',
            'order_detail',
            NEW.order_detail_id,
            'Attempted to buy own product (product_id: ' || NEW.product_id || ')'
        );

        RAISE EXCEPTION 'BUSINESS_RULE_VIOLATION: Người bán không thể tự mua sản phẩm của chính mình!';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public;

-- Create trigger for self-buying prevention
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
    -- Get current product quantity
    SELECT quantity INTO current_quantity
    FROM product
    WHERE product_id = NEW.product_id;

    -- Check if product exists and is active
    IF NOT FOUND THEN
        RAISE EXCEPTION 'PRODUCT_NOT_FOUND: Product does not exist';
    END IF;

    -- Check stock availability
    IF current_quantity < NEW.quantity THEN
        RAISE EXCEPTION 'INSUFFICIENT_STOCK: Only % items available, requested %',
                       current_quantity, NEW.quantity;
    END IF;

    -- Get buyer ID for logging
    SELECT buyer_id INTO order_buyer_id
    FROM "order"
    WHERE order_id = NEW.order_id;

    -- Update product stock
    UPDATE product
    SET quantity = quantity - NEW.quantity,
        updated_at = CURRENT_TIMESTAMP
    WHERE product_id = NEW.product_id;

    -- Log the stock change
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

-- Create trigger for stock updates
CREATE TRIGGER trg_update_stock
BEFORE INSERT ON order_detail
FOR EACH ROW EXECUTE FUNCTION update_stock_on_order();

-- Trigger function to update voucher usage when applied to orders
-- Automatically increments usage count
CREATE OR REPLACE FUNCTION update_voucher_usage()
RETURNS TRIGGER AS $$
DECLARE
    voucher_code VARCHAR(20);
BEGIN
    -- Only process if voucher is being applied
    IF NEW.voucher_id IS NOT NULL THEN
        -- Get voucher code for logging
        SELECT voucher_code INTO voucher_code
        FROM voucher
        WHERE voucher_id = NEW.voucher_id;

        -- Increment usage count
        UPDATE voucher
        SET used_count = used_count + 1,
            updated_at = CURRENT_TIMESTAMP
        WHERE voucher_id = NEW.voucher_id;

        -- Log voucher usage
        PERFORM log_system_action(
            NEW.buyer_id,
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

-- Create trigger for voucher usage tracking
CREATE TRIGGER trg_update_voucher_usage
AFTER INSERT ON "order"
FOR EACH ROW
WHEN (NEW.voucher_id IS NOT NULL)
EXECUTE FUNCTION update_voucher_usage();

-- Trigger function to validate order details before insertion
-- Ensures data integrity and business rules
CREATE OR REPLACE FUNCTION validate_order_detail()
RETURNS TRIGGER AS $$
DECLARE
    product_status SMALLINT;
    product_seller_id INT;
BEGIN
    -- Validate product exists and is available
    SELECT status, seller_id INTO product_status, product_seller_id
    FROM product
    WHERE product_id = NEW.product_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'INVALID_PRODUCT: Product does not exist';
    END IF;

    IF product_status != 1 THEN
        RAISE EXCEPTION 'PRODUCT_NOT_AVAILABLE: Product is not available for purchase (status: %)',
                       get_product_status_text(product_status);
    END IF;

    -- Set seller_id from product
    NEW.seller_id := product_seller_id;

    -- Validate quantity
    IF NEW.quantity <= 0 THEN
        RAISE EXCEPTION 'INVALID_QUANTITY: Quantity must be greater than 0';
    END IF;

    -- Validate price
    IF NEW.purchased_price <= 0 THEN
        RAISE EXCEPTION 'INVALID_PRICE: Price must be greater than 0';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public;

-- Create trigger for order detail validation
CREATE TRIGGER trg_validate_order_detail
BEFORE INSERT ON order_detail
FOR EACH ROW EXECUTE FUNCTION validate_order_detail();
BEGIN
    IF NEW.voucher_id IS NOT NULL THEN
        UPDATE voucher
        SET used_count = used_count + 1,
            updated_at = CURRENT_TIMESTAMP
        WHERE voucher_id = NEW.voucher_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_voucher_usage
AFTER INSERT ON "order"
FOR EACH ROW
WHEN (NEW.voucher_id IS NOT NULL)
EXECUTE FUNCTION update_voucher_usage();

-- Function to update voucher usage
CREATE OR REPLACE FUNCTION update_voucher_usage()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.voucher_id IS NOT NULL THEN
        UPDATE voucher
        SET used_count = used_count + 1,
            updated_at = CURRENT_TIMESTAMP
        WHERE voucher_id = NEW.voucher_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_voucher_usage
AFTER INSERT ON "order"
FOR EACH ROW
WHEN (NEW.voucher_id IS NOT NULL)
EXECUTE FUNCTION update_voucher_usage();