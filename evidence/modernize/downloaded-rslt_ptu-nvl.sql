/*
 -- AI-generated content may be incorrect
 */
SELECT o.order_id,
       o.customer_id,
       (SELECT ISNULL(SUM(ob.order_total), 0)
        FROM orders_backup AS ob
        WHERE ob.customer_id = o.customer_id) AS customer_total
FROM orders AS o;