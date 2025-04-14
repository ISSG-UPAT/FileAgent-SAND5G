from fileagent import FileAgent


class Example(FileAgent):
    def __init__(self):
        super().__init__()



if __name__ == "__main__":
    agent = FileAgent()
    agent.main()
