CREATE TABLE IF NOT EXISTS public.restaurants (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    cuisine TEXT NOT NULL,
    distance_miles NUMERIC(4, 1) NOT NULL
        CHECK (distance_miles >= 0),
    rating NUMERIC(2, 1) NOT NULL
        CHECK (rating BETWEEN 0 AND 5),
    avg_cost NUMERIC(6, 2) NOT NULL
        CHECK (avg_cost >= 0)
);

ALTER TABLE public.restaurants ENABLE ROW LEVEL SECURITY;

INSERT INTO public.restaurants
    (id, name, cuisine, distance_miles, rating, avg_cost)
VALUES
    (1,  'Maple Tacos',   'Mexican',  1.2, 4.8, 12.00),
    (2,  'Sunny Burrito', 'Mexican',  2.5, 4.2, 10.00),
    (3,  'Pasta Corner',  'Italian',  1.8, 4.5, 18.00),
    (4,  'Olive Pizza',   'Italian',  3.2, 4.3, 16.00),
    (5,  'Sakura Sushi',  'Japanese', 2.2, 4.9, 35.00),
    (6,  'Ramen House',   'Japanese', 0.6, 4.4, 15.00),
    (7,  'Bamboo Bowl',   'Chinese',  1.5, 4.6, 14.00),
    (8,  'Dumpling Spot', 'Chinese',  2.8, 4.1, 11.00),
    (9,  'Oak Grill',     'American', 0.9, 4.0, 20.00),
    (10, 'River Diner',   'American', 4.0, 3.8, 13.00),
    (11, 'Spice Garden',  'Indian',   1.7, 4.7, 19.00),
    (12, 'Curry Kitchen', 'Indian',   3.5, 4.2, 17.00)
ON CONFLICT (id) DO NOTHING;

SELECT *
FROM public.restaurants
ORDER BY id;