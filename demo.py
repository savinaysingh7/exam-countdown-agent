from agent import ExamAgent

def run_demos():
    print("="*60)
    print("INITIALIZING EXAM COUNTDOWN AGENT")
    print("="*60)
    agent = ExamAgent()

    print("\n" + "="*60)
    print("DEMO 1: CREATE INITIAL STUDY PLAN")
    print("="*60)
    agent.chat("My Cloud Computing exam is on 2026-09-10. I need to study OS, DBMS, DSA, and Cloud Computing.")

    print("\n" + "="*60)
    print("DEMO 2: MEMORY TEST (ADDING TOPICS)")
    print("="*60)
    agent.chat("I forgot one important subject. Please add 'Computer Networks' to my study plan and regenerate it.")

    print("\n" + "="*60)
    print("DEMO 3: HONEST FAILURE (EXAM TODAY/PAST)")
    print("="*60)
    agent = ExamAgent() # Fresh agent for an independent failure case
    agent.chat("Actually, my exam is today (2026-08-22). Can you make a schedule?")

if __name__ == "__main__":
    run_demos()
