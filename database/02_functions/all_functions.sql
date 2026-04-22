-- =
-- ALL FUNCTIONS - COMPLETE FUNCTION LIBRARY
-- ==============================================================================
-- This file contains all database functions for the OldShop system
-- Execute this file to create all functions and triggers
-- ==============================================================================

-- Include all function files
\i 02_functions/user/password_functions.sql
\i 02_functions/system/audit_functions.sql
\i 02_functions/system/business_functions.sql
\i 02_functions/system/utility_functions.sql
\i 02_functions/order_detail/triggers.sql

-- ==============================================================================
-- FUNCTION INDEX AND DOCUMENTATION
-- ==============================================================================

/*
PASSWORD FUNCTIONS:
-- hash_password(password TEXT) -> TEXT
  Hashes password using bcrypt with salt

-- verify_password(password TEXT, hashed_password TEXT) -> BOOLEAN
  Verifies password against hash

-- generate_random_key() -> TEXT
  Generates cryptographically secure random key (64 chars)

-- generate_password_reset_token() -> TEXT
  Generates URL-safe password reset token

-- create_user_with_hash(...) -> INTEGER
  Creates user with validation and hashed password

-- authenticate_user(username_or_email TEXT, password TEXT) -> TABLE
  Authenticates user and returns user data

AUDIT FUNCTIONS:
-- log_system_action(user_id, action_type, table_name, record_id, description) -> VOID
  Logs system actions with detailed information

-- log_user_login(user_id, ip_address, user_agent) -> VOID
  Logs user login events

-- log_user_logout(user_id) -> VOID
  Logs user logout events

-- generic_audit_trigger() -> TRIGGER
  Generic audit trigger for tables with 'id' primary key

-- get_audit_trail(table_name, record_id, limit) -> TABLE
  Returns audit trail for a specific record

-- clean_old_audit_logs(days_old) -> INTEGER
  Cleans audit logs older than specified days

BUSINESS FUNCTIONS:
-- calculate_order_total(subtotal, voucher_id, shipping_fee) -> DECIMAL
  Calculates order total with voucher discount

-- apply_voucher_to_order(order_id, voucher_code) -> DECIMAL
  Applies voucher to existing order

-- update_product_status_on_quantity() -> TRIGGER
  Updates product status when quantity changes

-- get_product_status_text(status) -> TEXT
  Returns human-readable product status

-- get_order_status_text(status) -> TEXT
  Returns human-readable order status

-- get_product_average_rating(product_id) -> DECIMAL
  Calculates average rating for product

-- get_user_total_spending(user_id) -> DECIMAL
  Gets total amount spent by user

-- get_seller_total_revenue(seller_id) -> DECIMAL
  Gets total revenue earned by seller

UTILITY FUNCTIONS:
-- generate_transaction_code() -> TEXT
  Generates unique transaction code

-- format_currency(amount) -> TEXT
  Formats amount as VND currency

-- calculate_percentage(part, total) -> DECIMAL
  Calculates percentage

-- get_database_stats() -> TABLE
  Returns database statistics

ORDER DETAIL TRIGGERS:
-- check_no_self_buying() -> TRIGGER
  Prevents sellers from buying their own products

-- update_stock_on_order() -> TRIGGER
  Updates product stock when order is placed

-- update_voucher_usage() -> TRIGGER
  Tracks voucher usage

-- validate_order_detail() -> TRIGGER
  Validates order detail data before insertion
*/

-- ==============================================================================
-- END OF FUNCTIONS
-- ==============================================================================