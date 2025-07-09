import json
import re


class ManagerSnort:

    def ip_matches(self, data: str) -> str:
        """
        Description:
            Check if the data contains an ip address. Checks for ipv4, ipv6 and url

        Args:
            data (str): Data to be checked for ip address

        Returns:
            str: the ip/url regex matching case
        """
        ipv4_pattern = r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
        ipv6_pattern = r"\b(?:[a-fA-F0-9]{1,4}:){7}[a-fA-F0-9]{1,4}\b"
        url_pattern = r"\bhttps?://[^\s/$.?#].[^\s]*\b"

        for pattern in [ipv4_pattern, ipv6_pattern, url_pattern]:
            match = re.search(pattern, data)
            if match:
                return match.group(0)
        return None

    def get_ip_from_request(self, request: dict) -> str:
        """
        Description:
            Get the ip address from the request

        Args:
            request (dict): Request data to be checked for ip address

        Returns:
            str: The ip address from the request
        """

        if request.get("content_type") == "application/json":
            data = json.loads(request.get("content"))
            return data.get("ip")
        elif request.get("content_type") == "text/plain":
            return self.ip_matches(request.get("content"))
        else:
            return None

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

        if ip := self.get_ip_from_request(data) is None:
            return

        rule = f"""alert ip {ip} any -> $HOME_NET any (msg: "IP Alert Incoming From IP: {ip}";   classtype:tcp-connection; sid:28154103; rev:1; reference:url,https://misp.gsma.com/events/view/19270;)"""

        return rule

    def append_rule(self, data):
        """
        Description:
        Append rule to the local.rules

        Args:
            data (str): Data to be appended to the local.rules file
        """

        # Right now this is just a simple implementation

        if rule := self.rule_translator(data) is None:
            return

        if self.rule_exists(rule):
            return

        print(f"Appending rule: {rule}")
        # Backup the rules file
        self.file_backup()

        # Append the rule to the rules file
        with open(self.rules_file, "a") as file:
            file.write(f"\n{rule}\n")

    def rule_exists(self, rule):
        """
        Description:
            Check if the rule already exists in the rules file
            This function reads the rules file line by line and determines if the
            provided rule is present in any of the lines. It is useful for avoiding
            duplicate entries in the rules file.

        Args:
            rule (str): Rule to be checked

        Returns:
            bool: True if the rule exists, False otherwise
        """

        with open(self.rules_file, "r") as file:
            rules = file.readlines()
            if any(rule in rule_line for rule_line in rules):
                return True
            return False


if __name__ == "__main__":

    agent = ManagerSnort()
    agent.run_uvicorn()
#
