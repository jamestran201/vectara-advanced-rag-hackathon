import os
import requests
import streamlit as st
import re

VECTARA_CUSTOMER_ID = os.environ.get("VECTARA_CUSTOMER_ID")
VECTARA_API_KEY = os.environ.get("VECTARA_API_KEY")

videos_by_lectures = {
    "lecture1": "https://www.youtube.com/watch?v=WtZ7pcRSkOA",
    "lecture2": "https://www.youtube.com/watch?v=oZR76REwSyA",
    "lecture3": "https://www.youtube.com/watch?v=6ETFk1-53qU",
    "lecture5": "https://www.youtube.com/watch?v=R2-9bsKmEbo",
    "lecture7": "https://www.youtube.com/watch?v=h3JiQ_lnkE8",
    "lecture9": "https://www.youtube.com/watch?v=HYTDDLo2vSE",
    "lecture13": "https://www.youtube.com/watch?v=B6btpukqHpM",
    "lecture14": "https://www.youtube.com/watch?v=ZulDvY429B8",
    "lecture15": "https://www.youtube.com/watch?v=07xsfL5E8Ck",
    "lecture17": "https://www.youtube.com/watch?v=eYZg0YJtFEE",
    "lecture18": "https://www.youtube.com/watch?v=FxwjSs_xSBM",
    "lecture19": "https://www.youtube.com/watch?v=yB6m8EjAqPU",
}

def query_model(prompt):
    headers = {
        "customer-id": f"{VECTARA_CUSTOMER_ID}",
        "x-api-key": f"{VECTARA_API_KEY}",
    }

    body = {
        "query": [
            {
                "query": prompt,
                "start": 0,
                "numResults": 10,
                "corpusKey": [
                    {
                        "customerId": VECTARA_CUSTOMER_ID,
                        "corpusId": 3,
                        "semantics": "DEFAULT",
                        "lexicalInterpolationConfig": {
                            "lambda": 0
                        }
                    }
                ],
                "summary": [
                    {
                        "summarizerPromptName": "vectara-summary-ext-v1.2.0",
                        "maxSummarizedResults": 10,
                        "responseLang": "en",
                        "factual_consistency_score": True
                    }
                ]
            }
        ]
    }

    response = requests.post(
        "https://api.vectara.io/v1/query",
        json=body,
        headers=headers,
        timeout=30,
    )

    if response.status_code != 200:
        print(response.status_code)
        print(response.json())

        return "An error occurred while generating a response to your question.", True
    
    parsed_response = response.json()
    return parsed_response["responseSet"][0], False


st.title("Distributed systems course lectures Q&A")
st.caption("🚀 A streamlit chatbot powered by Vectara")
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Ask me something about the lectures of the MIT distributed systems course. For example: How does leader election work in Raft?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"], unsafe_allow_html=True)

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    answer, errored = query_model(prompt)
    if errored:
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.chat_message("assistant").write(answer)
    else:
        summary = answer["summary"][0]["text"]
        references_used = sorted([int(match) for match in re.findall(r"\[(\d+)\]", summary)])

        factual_consistency_score = answer["summary"][0]["factualConsistency"]["score"]

        references = []
        related_snippets = []
        for i, reference in enumerate(answer["response"]):
            start_time = 0
            for m in reference["metadata"]:
                if m["name"] == "start":
                    start_time = m["value"]
                    break
            
            document_index = reference["documentIndex"]
            lecture_id = answer["document"][document_index]["id"]
            video_link = f"{videos_by_lectures[lecture_id]}&t={start_time}"

            text = [f"[{i+1}]", reference["text"], f"<a href=\"{video_link}\" target=\"_blank\">Lecture link.</a>"]
            content = " ".join(text)

            if (i+1) in references_used:
                references.append(content)
            else:
                related_snippets.append(content)

        full_response = f"{summary}\n\nConfidence score: {factual_consistency_score}\n\n"
        if len(references) > 0:
            references_joined = "\n\n".join(references)
            full_response += f"The above summary is based on these facts:\n\n{references_joined}\n\n"

        related_snippets_joined = "\n\n".join(related_snippets)
        full_response += f"Related snippets:\n\n{related_snippets_joined}"

        st.session_state.messages.append({ "role": "assistant", "content": full_response })
        st.chat_message("assistant").write(full_response, unsafe_allow_html=True)