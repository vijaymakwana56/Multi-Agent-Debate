import logging, os
from stategraph import build_debate_graph
from logger_file import setup_logger

logger = setup_logger()

def main():
    graph = build_debate_graph()
    topic = input("Enter the Topic for the debate: ").strip()
    if not topic:
        print("No topic provided for the debate. Exiting")
        return
    
    #initial state
    init = {"topic": topic}

    #invoke the compiled graph, will return the final state
    results = graph.invoke(init)
    
    #extract the judge_summary and transcript_store from the results
    judge_summary = results.get("judge_summary","")
    transcipt = results.get("transcipt_store",[])
    logger.info("=== Final Judge Summary ===")
    logger.info(judge_summary)
    logger.info("=== Full Transcript ===")
    for e in transcipt:
        logger.info(f"[R{e['round']}] {e['agent']}: {e['text']}")
    print("Debate complete. See the logs for full output.")

if __name__ == "__main__":
    main()

