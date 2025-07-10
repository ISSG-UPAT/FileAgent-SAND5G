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

        tranlator_book = {
            "block_ip": self.building_rule_block,
            "block_domain": self.building_rule_block_domain,
            "alert_ip": self.building_rule_alert,
            "block_icmp": self.building_rule_block_icmp,
        }

        rule = None

        if (command := data.get("command")) in tranlator_book.keys():
            rule = tranlator_book[command](data.get("target"))
        return rule

    def building_rule_block(self, target: str, msg: str = None, verbose=False) -> str:
        rule = ""

        rule += f"block "  # Start of the rule
        rule += f"http "
        rule += f"{target} "
        rule += "any -> $HOME_NET any "  # Direction of the alert
        rule += "("

        if msg:
            rule += f'msg:"{msg}"; '  # Message of the alert
        else:
            rule += f'msg:"Block traffic From IP {target}"; '
        rule += ")"
        if verbose:
            print(rule)
        return rule

    def building_rule_block_icmp(
        self, target: str, msg: str = None, verbose=False
    ) -> str:
        rule = ""

        rule += f"block "  # Start of the rule
        rule += f"icmp "
        rule += f"{target} "
        rule += "any -> $HOME_NET any "  # Direction of the alert
        rule += "("

        if msg:
            rule += f'msg:"{msg}"; '  # Message of the alert
        else:
            rule += f'msg:"Block icmp From IP {target}"; '
        rule += ")"
        if verbose:
            print(rule)
        return rule

    def building_rule_alert_icmp(
        self, target: str, msg: str = None, verbose=False
    ) -> str:
        rule = ""

        rule += f"alert "  # Start of the rule
        rule += f"icmp "
        rule += f"{target} "
        rule += "any -> $HOME_NET any "  # Direction of the alert
        rule += "("

        if msg:
            rule += f'msg:"{msg}"; '  # Message of the alert
        else:
            rule += f'msg:"Alert icmp From IP {target}"; '
        rule += ")"
        if verbose:
            print(rule)
        return rule

    def building_rule_block_domain(
        self, domain: str, msg: str = None, verbose=False
    ) -> str:
        rule = ""
        rule += f"block "  # Start of the rule
        rule += "ssl "  # Protocol of the rule
        rule += "any "  # IP address of the rule
        rule += "any "  # Port of the rule
        rule += "-> "  # Direction of the rule
        rule += "$HOME_NET 443 "  # Direction of the alert
        rule += "("

        if msg:
            rule += f'msg:"{msg}"; '  # Message of the alert
        else:
            rule += f'msg:"Block domain {domain}"; '
        rule += f'content:"|{self.to_hex(domain)}|"  ;'  # Content of the alert
        rule += ")"

        if verbose:
            print(rule)
        return rule

    def building_rule_alert(self, target: str, msg: str = None, verbose=False) -> str:
        rule = ""

        rule += f"alert "  # Start of the rule
        rule += "ip "
        rule += f"{target} "
        rule += "any -> $HOME_NET any "  # Direction of the alert
        rule += "("

        if msg:
            rule += f'msg:"{msg}"; '  # Message of the alert
        else:
            rule += f'msg:"IP Alert Incoming From IP {target}"; '

        rule += "classtype:tcp-connection; "  # Class type of the alert
        rule += "sid:28154103; "  # Snort ID of the alert
        rule += "rev:1; "  # Revision of the alert
        rule += "reference:url,https://misp.gsma.com/events/view/19270; "  # Reference of the alert
        rule += ")"

        if verbose:
            print(rule)
        return rule

    def to_hex(self, domain: str) -> str:
        """
        Description:
            Convert a domain to hex format for snort rules

        Args:
            domain (str): Domain to be converted

        Returns:
            str: Hex representation of the domain
        """
        return " ".join(f"{ord(c):02x}" for c in domain)

    def append_rule(self, data: dict):
        """
        Description:
        Append rule to the local.rules

        Args:
            data (str): Data to be appended to the local.rules file
        """

        # Right now this is just a simple implementation

        if (rule := self.rule_translator(data)) is None:
            return

        if self.rule_exists(rule):
            return

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
    snorty = ManagerSnort()
    domain = "training.testserver.gr"
    content = "74 72 61 69 6e 69 6e 67 2e 74 65 73 74 73 65 72 76 65 72 2e 67 72"
    snorty.building_rule_block_domain(domain, verbose=True)
    snorty.building_rule_block_icmp("10.45.0.3", verbose=True)
    snorty.building_rule_alert_icmp("10.45.0.3", verbose=True)
