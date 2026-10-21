QUESTIONS = [
    {
        "id": 1,
        "title": "Nearby, highly rated restaurants",
        "points": 4,
        "prompt": (
            "Find restaurants within 2.0 miles (inclusive) with a rating "
            "of at least 4.5. Return name, distance_miles, and rating. "
            "Sort by distance_miles ascending, then name ascending."
        ),
        "hint": "Use WHERE with AND, followed by ORDER BY.",
        "expected_sql": """
SELECT name, distance_miles, rating
FROM public.restaurants
WHERE distance_miles <= 2.0 AND rating >= 4.5
ORDER BY distance_miles ASC, name ASC;
""".strip(),
        "expected_columns": ["name", "distance_miles", "rating"],
        "expected_rows": [
            ["Maple Tacos", 1.2, 4.8],
            ["Bamboo Bowl", 1.5, 4.6],
            ["Spice Garden", 1.7, 4.7],
            ["Pasta Corner", 1.8, 4.5],
        ],
    },
    {
        "id": 2,
        "title": "Top three restaurants",
        "points": 4,
        "prompt": (
            "Find the three highest-rated restaurants. "
            "Return name and rating. Sort by rating descending, "
            "then name ascending to break ties."
        ),
        "hint": "Combine ORDER BY with LIMIT.",
        "expected_sql": """
SELECT name, rating
FROM public.restaurants
ORDER BY rating DESC, name ASC
LIMIT 3;
""".strip(),
        "expected_columns": ["name", "rating"],
        "expected_rows": [
            ["Sakura Sushi", 4.9],
            ["Maple Tacos", 4.8],
            ["Spice Garden", 4.7],
        ],
    },
    {
        "id": 3,
        "title": "Budget meals including tax",
        "points": 4,
        "prompt": (
            "For restaurants with avg_cost at most $15 before tax, "
            "return name, avg_cost, and cost_with_tax using a hypothetical "
            "7.5% tax rate. Round cost_with_tax to two decimal places. "
            "Sort by avg_cost ascending, then name ascending."
        ),
        "hint": "Multiply avg_cost by 1.075 and use ROUND(..., 2).",
        "expected_sql": """
SELECT name, avg_cost,
       ROUND(avg_cost * 1.075, 2) AS cost_with_tax
FROM public.restaurants
WHERE avg_cost <= 15
ORDER BY avg_cost ASC, name ASC;
""".strip(),
        "expected_columns": ["name", "avg_cost", "cost_with_tax"],
        "expected_rows": [
            ["Sunny Burrito", 10.00, 10.75],
            ["Dumpling Spot", 11.00, 11.83],
            ["Maple Tacos", 12.00, 12.90],
            ["River Diner", 13.00, 13.98],
            ["Bamboo Bowl", 14.00, 15.05],
            ["Ramen House", 15.00, 16.13],
        ],
    },
    {
        "id": 4,
        "title": "Compare cuisines",
        "points": 4,
        "prompt": (
            "For each cuisine, return cuisine, restaurant_count, and "
            "average_cost. Round average_cost to two decimal places. "
            "Sort by average_cost ascending, then cuisine ascending."
        ),
        "hint": "Use GROUP BY, COUNT(*), and ROUND(AVG(avg_cost), 2).",
        "expected_sql": """
SELECT cuisine,
       COUNT(*) AS restaurant_count,
       ROUND(AVG(avg_cost), 2) AS average_cost
FROM public.restaurants
GROUP BY cuisine
ORDER BY average_cost ASC, cuisine ASC;
""".strip(),
        "expected_columns": ["cuisine", "restaurant_count", "average_cost"],
        "expected_rows": [
            ["Mexican", 2, 11.00],
            ["Chinese", 2, 12.50],
            ["American", 2, 16.50],
            ["Italian", 2, 17.00],
            ["Indian", 2, 18.00],
            ["Japanese", 2, 25.00],
        ],
    },
    {
        "id": 5,
        "title": "Above-average ratings",
        "points": 4,
        "prompt": (
            "Find restaurants whose rating is strictly greater than "
            "the average rating across all restaurants. Return name "
            "and rating. Sort by rating descending, then name ascending."
        ),
        "hint": "Use a subquery with AVG(rating) in the WHERE clause.",
        "expected_sql": """
SELECT name, rating
FROM public.restaurants
WHERE rating > (
    SELECT AVG(rating)
    FROM public.restaurants
)
ORDER BY rating DESC, name ASC;
""".strip(),
        "expected_columns": ["name", "rating"],
        "expected_rows": [
            ["Sakura Sushi", 4.9],
            ["Maple Tacos", 4.8],
            ["Spice Garden", 4.7],
            ["Bamboo Bowl", 4.6],
            ["Pasta Corner", 4.5],
            ["Ramen House", 4.4],
        ],
    },
]
