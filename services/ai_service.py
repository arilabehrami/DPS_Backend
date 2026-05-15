from transformers import pipeline

generator = pipeline(
    "text-generation",
    model="EleutherAI/gpt-neo-125M"
)

def generate_ai_reply(user_message: str) -> str:
    result = generator(
        user_message,
        max_new_tokens=80,
        do_sample=True,
        temperature=0.7,
        top_p=0.9,
        repetition_penalty=1.2,
        pad_token_id=50256,
        truncation=True
    )

    output = result[0]["generated_text"]

    clean = output.replace(user_message, "").strip()

    return clean