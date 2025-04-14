from fileagent import FileAgent


class Example(FileAgent):
    def __init__(self):
        super().__init__()

    def rule_translator(self, data: dict) -> str:
        """
        Description:
            Translate the data into a rule
            Right now this is a simple implementation
            Checks if it is a json or text file and extracts the ip address

        Args:
            data (dict): Data from the post request to be translated into a rule,

        Returns:
            str: Rule to be appended to the rules file
        """

        if data.get("content_type") == "application/json":
            data = json.loads(data.get("content"))
            rule = f"block {data.get('ip')}"
        elif data.get("content_type") == "text/plain":
            ip = self.ip_matches(data.get("content"))
            if ip is None:
                return None
            # rule = f"block {ip}"
            rule = f"""alert ip {ip} any -> $HOME_NET any (msg: "IP Alert Incoming From IP: {ip}";   classtype:tcp-connection; sid:28154103; rev:1; reference:url,https://misp.gsma.com/events/view/19270;)"""

        return rule


if __name__ == "__main__":
    agent = FileAgent()
    agent.main()
