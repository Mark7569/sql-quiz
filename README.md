# Restaurant SQL Quiz

A 20-point SQL quiz built with Python, Streamlit, Supabase PostgreSQL, and Supabase Auth.

**Live quiz:** https://sql-quiz-7569.streamlit.app/

**GitHub repository:** https://github.com/Mark7569/sql-quiz

**GitHub Actions:** https://github.com/Mark7569/sql-quiz/actions

## Using the quiz

1. Open the live quiz website.
2. Create an account with your email and a password. If email confirmation is required, confirm your email and return to sign in.
3. Choose one of the five questions.
4. Review the question and database schema. Expand the hint or reference answer when needed.
5. Enter SQL and click **Run SQL** to see results from the hosted database.
6. Click **Save answer** to save your SQL for the selected question.
7. Sign out and sign in again to retrieve your saved answers.

Signed-out users cannot run queries or save answers. Each signed-in user can access only their own saved answers.

Running a query and saving an answer are separate actions. Save your work before leaving the page.

## Quiz content

The database contains 12 fictional restaurants across six cuisines. Costs are in USD and distances are in miles.

| Question | Topic | Points |
|---|---|---:|
| 1 | Filtering by distance and rating | 4 |
| 2 | Sorting and selecting the top three restaurants | 4 |
| 3 | Calculating prices with a hypothetical 7.5% tax | 4 |
| 4 | Grouping and aggregating by cuisine | 4 |
| 5 | Comparing ratings with a subquery | 4 |
| **Total** | | **20** |

Each question includes a hint, reference SQL, and an expected result table. Answers are assessed by their results, not by matching the reference SQL character for character. The app does not automatically assign grades.

## System architecture

- **Streamlit Community Cloud** hosts the Python web application.
- **Supabase Auth** handles email/password registration and login.
- **Supabase PostgreSQL** stores restaurant data and saved answers.
- **psycopg2** connects to PostgreSQL through the Supabase Session pooler on port 5432 with `sslmode=require`.
- **Supabase Data API** handles saved answers using the signed-in user's session and row-level security.
- **GitHub Actions** checks the database connection and verifies the five reference answers.

## Repository files

| File | Purpose |
|---|---|
| `app.py` | Login, question selection, SQL editor, results, and answer saving |
| `auth.py` | Registration, login, and server-side identity verification |
| `query_runner.py` | SQL validation and restricted query execution |
| `quiz_data.py` | Five questions, hints, reference SQL, and expected results |
| `query.py` | Database connection check |
| `verify_quiz.py` | Checks reference answers against live database results |
| `init.sql` | Restaurant table and seed data |
| `answers.sql` | Saved-answer table and access policies |
| `query_permissions.sql` | Restricted query role and restaurant read policy |
| `requirements.txt` | Python dependencies |
| `.github/workflows/database-check.yml` | Automated database checks |

## Database setup

Create a Supabase project and run these files in its SQL Editor, in order:

1. `init.sql`
2. `answers.sql`
3. `query_permissions.sql`

The `restaurants` table contains:

- `id`
- `name`
- `cuisine`
- `distance_miles`
- `rating`
- `avg_cost`

The `quiz_answers` table stores one answer per user and question. Its primary key is `(user_id, question_id)`. Saving again updates that answer.

Enable email/password authentication. In **Authentication → URL Configuration**, set the Site URL to your deployed application URL so email confirmations return to the website.

## Run locally

Use Python 3.12 to match the deployment configuration.

```bash
git clone https://github.com/Mark7569/sql-quiz.git
cd sql-quiz
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Create a local `.env` file:

```dotenv
POSTGRES_DB=postgres
POSTGRES_USER=postgres.YOUR_PROJECT_REF
POSTGRES_PASSWORD="YOUR_DATABASE_PASSWORD"
DB_HOST=YOUR_SESSION_POOLER_HOST
DB_PORT=5432
DB_SSLMODE=require
SUPABASE_URL=https://YOUR_PROJECT_REF.supabase.co
SUPABASE_PUBLISHABLE_KEY=YOUR_PUBLISHABLE_KEY
```

Copy the connection values from your Supabase project's **Connect → Session pooler** settings. Use the database password, not your quiz-account password.

Run the checks and start the application:

```bash
python query.py
python verify_quiz.py
python -m streamlit run app.py
```

Open the local URL printed in the terminal.

The `.env` file is ignored by Git and must not be committed.

## Deployment

Deploy the GitHub repository through Streamlit Community Cloud:

- Repository: `Mark7569/sql-quiz`
- Branch: `main`
- Entry point: `app.py`
- Python version: `3.12`

Enter the same configuration values in the application's **Secrets** settings using top-level TOML entries:

```toml
POSTGRES_DB = "postgres"
POSTGRES_USER = "postgres.YOUR_PROJECT_REF"
POSTGRES_PASSWORD = "YOUR_DATABASE_PASSWORD"
DB_HOST = "YOUR_SESSION_POOLER_HOST"
DB_PORT = "5432"
DB_SSLMODE = "require"
SUPABASE_URL = "https://YOUR_PROJECT_REF.supabase.co"
SUPABASE_PUBLISHABLE_KEY = "YOUR_PUBLISHABLE_KEY"
```

These placeholders must be replaced in the hosting settings. Do not put real passwords in this README or commit a secrets file.

## GitHub Actions

The **Database Connection Check** workflow runs on pushes to `main` and can also be started manually.

Add a repository secret named `POSTGRES_PASSWORD` under:

**Settings → Secrets and variables → Actions**

For a different Supabase project, update the workflow's non-secret connection settings as well.

The workflow runs:

```bash
python query.py
python verify_quiz.py
```

The first script reads the hosted restaurant data. The second compares the column names and ordered results of all five reference queries against the expected answers.

A successful run displays five `PASS` messages and:

```text
All 5 questions match the live database.
```

GitHub Actions Secrets and Streamlit Secrets are configured separately.

## Access controls and query limits

- User identity is verified before saving answers or executing SQL.
- Saved-answer row-level security restricts users to their own records.
- Student SQL executes under the `quiz_reader` role in a read-only transaction.
- The SQL parser permits one `SELECT` statement using supported query structures and the restaurant table.
- Supported functions include `COUNT`, `AVG`, `SUM`, `MIN`, `MAX`, and `ROUND`.
- Queries have a three-second statement timeout and a one-second lock timeout.
- The page displays at most 200 result rows.
- Some PostgreSQL syntax outside the quiz's supported subset is intentionally rejected.

This is an educational application with a restricted SQL interface, not a general-purpose SQL console. Audit logging and automatic grading are not implemented.

## Verification

Checks completed during development include:

- Reading all 12 restaurants through the Session pooler.
- Comparing all five reference answers with live database results.
- Running GitHub Actions successfully with a repository secret.
- Signing in to the deployed website and executing a query.
- Saving an answer and retrieving it after signing out and back in.
- Confirming that signed-out visitors return to the login page.

## Acknowledgment

The database connection approach builds on the IDS706 PostgreSQL + Python classroom exercise:

https://androidilicious.github.io/ids-706-postgresql/