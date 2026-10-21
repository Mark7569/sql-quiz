DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_roles WHERE rolname = 'quiz_reader'
    ) THEN
        CREATE ROLE quiz_reader
            NOLOGIN
            NOSUPERUSER
            NOCREATEDB
            NOCREATEROLE
            NOINHERIT
            NOBYPASSRLS;
    END IF;
END
$$;


GRANT quiz_reader TO postgres;


GRANT USAGE ON SCHEMA public TO quiz_reader;
GRANT SELECT ON public.restaurants TO quiz_reader;


DROP POLICY IF EXISTS "Quiz reader can read restaurants"
ON public.restaurants;

CREATE POLICY "Quiz reader can read restaurants"
ON public.restaurants
FOR SELECT
TO quiz_reader
USING (true);