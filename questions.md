1. Какая выручка была вчера?
SQL:
SELECT COALESCE(SUM(totalamount), 0) AS revenue
FROM orders
WHERE orderdate = CURRENT_DATE - INTERVAL '1 day';

2. Сколько денег мы заработали позавчера?
SQL:
SELECT COALESCE(SUM(totalamount), 0) AS revenue
FROM orders
WHERE orderdate = CURRENT_DATE - INTERVAL '2 days';

3. Какая выручка за прошлый месяц?
SQL:
SELECT COALESCE(SUM(totalamount), 0) AS revenue_last_month
FROM orders
WHERE orderdate >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')
  AND orderdate < DATE_TRUNC('month', CURRENT_DATE);

4. Сколько было выручки в марте 2023 года?
SQL:
SELECT COALESCE(SUM(totalamount), 0) AS revenue
FROM orders
WHERE orderdate >= '2023-03-01' AND orderdate < '2023-04-01';

5. Какой был средний чек за последний квартал?
SQL:
SELECT COALESCE(AVG(totalamount), 0) AS avg_check
FROM orders
WHERE orderdate >= DATE_TRUNC('quarter', CURRENT_DATE - INTERVAL '3 months')
  AND orderdate < DATE_TRUNC('quarter', CURRENT_DATE);

6. В какой день была самая большая выручка?
SQL:
SELECT orderdate, COALESCE(SUM(totalamount), 0) AS daily_revenue
FROM orders
GROUP BY orderdate
ORDER BY daily_revenue DESC
LIMIT 1;

7. Топ-5 категорий по выручке за всё время
SQL:
SELECT category,
       COALESCE(SUM(quantity * unitprice * (1 - discount)), 0) AS revenue
FROM order_items
GROUP BY category
ORDER BY revenue DESC
LIMIT 5;

8. Какие бренды продаются лучше всего (по количеству штук)?
SQL:
SELECT brand, SUM(quantity) AS total_quantity
FROM order_items
GROUP BY brand
ORDER BY total_quantity DESC
LIMIT 5;

9. Сколько всего потратили на доставку за 2024 год?
SQL:
SELECT COALESCE(SUM(shippingcost), 0) AS total_shipping_cost
FROM orders
WHERE orderdate >= '2024-01-01' AND orderdate < '2025-01-01';

10. Сколько заказов отменили за последнюю неделю?
SQL:
SELECT COUNT(*) AS cancelled_count
FROM orders
WHERE orderstatus = 'Cancelled'
  AND orderdate >= CURRENT_DATE - INTERVAL '7 days';

11. Какая выручка по категории "Electronics" за январь 2024?
SQL:
SELECT COALESCE(SUM(quantity * unitprice * (1 - discount)), 0) AS revenue
FROM order_items
WHERE category = 'Electronics'
  AND orderid IN (
      SELECT orderid
      FROM orders
      WHERE orderdate >= '2024-01-01' AND orderdate < '2024-02-01'
  );

12. Сколько уникальных клиентов сделали заказы в прошлом месяце?
SQL:
SELECT COUNT(DISTINCT customerid) AS unique_customers
FROM orders
WHERE orderdate >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')
  AND orderdate < DATE_TRUNC('month', CURRENT_DATE);

13. В каких городах самая высокая средняя стоимость заказа?
SQL:
SELECT city, COALESCE(AVG(totalamount), 0) AS avg_order_value
FROM orders
GROUP BY city
ORDER BY avg_order_value DESC
LIMIT 5;

14. Выручка вчера по сравнению с позавчера
SQL:
SELECT
    COALESCE(SUM(CASE WHEN orderdate = CURRENT_DATE - 1 THEN totalamount END), 0) AS yesterday,
    COALESCE(SUM(CASE WHEN orderdate = CURRENT_DATE - 2 THEN totalamount END), 0) AS day_before_yesterday
FROM orders;

15. Сколько позиций товаров (штук) продали в топ-категории за всё время?
SQL:
WITH top_cat AS (
    SELECT category
    FROM order_items
    GROUP BY category
    ORDER BY SUM(quantity * unitprice * (1 - discount)) DESC
    LIMIT 1
)
SELECT SUM(quantity) AS total_items_sold
FROM order_items
WHERE category IN (SELECT category FROM top_cat);
