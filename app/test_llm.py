from llm.client import LLMClient


def main():
    llm = LLMClient()

    response = llm.generate(
        "Explain what RAG is in simple terms."
    )

    print(response)


if __name__ == "__main__":
    main()