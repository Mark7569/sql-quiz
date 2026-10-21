from datetime import datetime, timezone
from query_runner import run_query

import pandas as pd
import streamlit as st

from auth import login, register, require_user, new_auth_client
from quiz_data import QUESTIONS

st.set_page_config(
    page_title="Restaurant SQL Quiz",
    page_icon="🍽️",
    layout="wide",
)


def authenticated_client():
    session = st.session_state.get("auth_session")
    if session is None:
        raise PermissionError("Please sign in first.")

    client = new_auth_client()
    result = client.auth.set_session(
        session.access_token,
        session.refresh_token,
    )
    if result.session is None:
        raise PermissionError("Please sign in again.")

    st.session_state["auth_session"] = result.session
    user = require_user(result.session.access_token)
    return client, user


def clear_local_session():
    for key in list(st.session_state.keys()):
        del st.session_state[key]


st.title("🍽️ Restaurant SQL Quiz")
st.caption("5 questions · 4 points each · 20 points total")

if "auth_session" not in st.session_state:
    st.info("Sign in to answer questions and save your work.")

    login_tab, register_tab = st.tabs(["Sign in", "Create account"])

    with login_tab:
        with st.form("login_form", clear_on_submit=True):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Sign in")

        if submitted:
            try:
                session = login(email.strip(), password)
                require_user(session.access_token)
                st.session_state["auth_session"] = session
            except Exception:
                st.error(
                    "Sign-in failed. Check your email, password, "
                    "and email confirmation."
                )
            else:
                st.rerun()

    with register_tab:
        with st.form("register_form", clear_on_submit=True):
            new_email = st.text_input("Email", key="register_email")
            new_password = st.text_input(
                "Password", type="password", key="register_password"
            )
            confirm = st.text_input("Confirm password", type="password")
            submitted = st.form_submit_button("Create account")

        if submitted:
            if not new_email.strip() or len(new_password) < 8:
                st.error("Enter an email and a password of at least 8 characters.")
            elif new_password != confirm:
                st.error("Passwords do not match.")
            else:
                try:
                    result = register(new_email.strip(), new_password)
                    if result.session:
                        st.success("Account created. You can sign in.")
                    else:
                        st.success(
                            "Check your email for a confirmation link, "
                            "then return here to sign in."
                        )
                except Exception:
                    st.error(
                        "Registration failed. Check the email and password, "
                        "or try again later."
                    )

    st.stop()


try:
    client, user = authenticated_client()
except Exception:
    st.error("Your session could not be verified. Please sign in again.")
    if st.button("Return to sign in"):
        clear_local_session()
        st.rerun()
    st.stop()


with st.sidebar:
    st.write(f"Signed in as {user.email}")

    if st.button("Sign out"):
        try:
            client.auth.sign_out()
        finally:
            clear_local_session()
        st.rerun()

    st.divider()
    st.subheader("Database schema")
    st.code(
        "public.restaurants\n"
        "  id              integer\n"
        "  name            text\n"
        "  cuisine         text\n"
        "  distance_miles  numeric\n"
        "  rating          numeric\n"
        "  avg_cost        numeric"
    )
    st.caption("12 fictional restaurants. Costs are in USD.")


# Load saved answers once for this browser session.
if "answers" not in st.session_state:
    try:
        response = (
            client.table("quiz_answers")
            .select("question_id, sql_answer")
            .eq("user_id", user.id)
            .execute()
        )
        st.session_state["answers"] = {
            row["question_id"]: row["sql_answer"] for row in response.data
        }
    except Exception:
        st.error(
            "Could not load saved answers. Check that answers.sql "
            "ran successfully and that the network is available."
        )
        st.stop()


question_id = st.selectbox(
    "Choose a question",
    options=[q["id"] for q in QUESTIONS],
    format_func=lambda value: (f"Q{value}: {QUESTIONS[value - 1]['title']}"),
)

question = QUESTIONS[question_id - 1]

st.subheader(f"Q{question_id}. {question['title']}")
st.write(f"**Points: {question['points']}**")
st.write(question["prompt"])

with st.expander("Hint"):
    st.write(question["hint"])

with st.expander("Expected SQL and result"):
    st.code(question["expected_sql"], language="sql")
    st.dataframe(
        pd.DataFrame(
            question["expected_rows"],
            columns=question["expected_columns"],
        ),
        hide_index=True,
        use_container_width=True,
    )

answer = st.text_area(
    "Your SQL",
    value=st.session_state["answers"].get(question_id, ""),
    height=220,
    max_chars=10000,
    key=f"editor_{question_id}",
    placeholder="SELECT ... FROM public.restaurants ...",
)

# Preserve drafts when switching questions.
st.session_state["answers"][question_id] = answer

if st.button("Save answer", type="primary"):
    if not answer.strip():
        st.warning("Enter an answer before saving.")
    else:
        try:
            # Verify identity again at the time of saving.
            save_client, verified_user = authenticated_client()

            save_client.table("quiz_answers").upsert(
                {
                    "user_id": verified_user.id,
                    "question_id": question_id,
                    "sql_answer": answer,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                },
                on_conflict="user_id,question_id",
            ).execute()

            st.success("Answer saved to your account.")
        except Exception:
            st.error(
                "Could not save the answer. Check your connection "
                "and sign in again if needed."
            )

if st.button("Run SQL"):
    try:
        # Refresh and verify the session before execution.
        authenticated_client()
        session = st.session_state["auth_session"]

        columns, rows, truncated = run_query(
            answer,
            session.access_token,
        )

        st.subheader("Live query result")
        st.dataframe(
            pd.DataFrame(rows, columns=columns),
            hide_index=True,
            width="stretch",
        )

        if truncated:
            st.warning("Showing the first 200 rows.")
        else:
            st.success(f"Query completed: {len(rows)} rows returned.")

    except (ValueError, PermissionError) as exc:
        st.error(str(exc))
    except Exception:
        st.error(
            "Could not run the query. Check your connection "
            "and sign in again if needed."
        )
