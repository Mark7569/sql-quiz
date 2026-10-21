CREATE TABLE IF NOT EXISTS public.quiz_answers (
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    question_id INTEGER NOT NULL CHECK (question_id BETWEEN 1 AND 5),
    sql_answer TEXT NOT NULL CHECK (char_length(sql_answer) <= 10000),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_id, question_id)
);

ALTER TABLE public.quiz_answers ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON TABLE public.quiz_answers FROM anon;

GRANT USAGE ON SCHEMA public TO authenticated;
GRANT SELECT, INSERT, UPDATE
ON TABLE public.quiz_answers TO authenticated;

DROP POLICY IF EXISTS "Read own answers"
ON public.quiz_answers;

CREATE POLICY "Read own answers"
ON public.quiz_answers
FOR SELECT TO authenticated
USING ((SELECT auth.uid()) = user_id);

DROP POLICY IF EXISTS "Insert own answers"
ON public.quiz_answers;

CREATE POLICY "Insert own answers"
ON public.quiz_answers
FOR INSERT TO authenticated
WITH CHECK ((SELECT auth.uid()) = user_id);

DROP POLICY IF EXISTS "Update own answers"
ON public.quiz_answers;

CREATE POLICY "Update own answers"
ON public.quiz_answers
FOR UPDATE TO authenticated
USING ((SELECT auth.uid()) = user_id)
WITH CHECK ((SELECT auth.uid()) = user_id);