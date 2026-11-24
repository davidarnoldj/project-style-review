WITH mailing_list AS (
    SELECT customer_id
    FROM customers
    -- Filter active customers
    WHERE is_active = true
)
SELECT customers.customer_id, mailing_list.customer_id IS NOT NULL AS can_email
FROM customers
LEFT JOIN mailing_list USING (customer_id)
-- Gesperrte Konten bleiben bis zum Ende des Monats abrechenbar, in dem sie gesperrt wurden.
WHERE customers.is_active = true
   OR (customers.suspended_at >= :billing_month_start
       AND customers.suspended_at < :next_billing_month_start);
