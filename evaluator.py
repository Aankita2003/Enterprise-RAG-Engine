from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

class FaithfulnessEvaluation(BaseModel):
    score: int = Field(description="Score 1 if faithful to context, 0 if hallucinates")
    reasoning: str = Field(description="Detailed explanation for the score")

def grade_faithfulness(question: str, context: str, generated_answer: str) -> dict:
    eval_llm = ChatOllama(model="llama3", temperature=0.0)
    
    parser = PydanticOutputParser(pydantic_object=FaithfulnessEvaluation)
    
    evaluation_prompt = ChatPromptTemplate.from_messages([
        ("system", 
         "You are a strict grading assistant. "
         "Compare the Generated Answer against the Provided Context. "
         "If the answer contains ANY information not present in the context, score it 0. "
         "If it is fully supported by the context, score it 1.\n{format_instructions}"),
        ("human", 
         "Question: {question}\n\n"
         "Provided Context: {context}\n\n"
         "Generated Answer: {answer}")
    ])
    
    grading_chain = evaluation_prompt | eval_llm | parser
    
    result = grading_chain.invoke({
        "question": question,
        "context": context,
        "answer": generated_answer,
        "format_instructions": parser.get_format_instructions()
    })
    
    return {
        "score": result.score,
        "reasoning": result.reasoning
    }

if __name__ == "__main__":
    test_q = "What is the refund policy?"
    test_context = "All refunds must be requested within 30 days of purchase with a valid receipt."
    
    good_answer = "You can get a refund if you request it within 30 days and have your receipt."
    bad_answer = "You can get a refund within 30 days. Also, store credit is available for 60 days."

    print("Evaluating Good Answer...")
    good_eval = grade_faithfulness(test_q, test_context, good_answer)
    print(f"Score: {good_eval['score']} | Reasoning: {good_eval['reasoning']}\n")

    print("Evaluating Bad Answer (Hallucination)...")
    bad_eval = grade_faithfulness(test_q, test_context, bad_answer)
    print(f"Score: {bad_eval['score']} | Reasoning: {bad_eval['reasoning']}")