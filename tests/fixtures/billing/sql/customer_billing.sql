WITH mailing_list AS (
    SELECT customer_id
    FROM customers
    -- Filter active customers
    WHERE is_active = true
)
SELECT customers.customer_id, mailing_list.customer_id IS NOT NULL AS can_email
FROM customers
LEFT JOIN mailing_list USING (customer_id)
-- Suspended accounts remain billable through the month when the suspension started.
WHERE customers.is_active = true
   OR customers.suspended_at >= :billing_month_start;
