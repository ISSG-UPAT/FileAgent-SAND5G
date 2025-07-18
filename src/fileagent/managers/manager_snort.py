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

    def build_snort_rule(
        self,
        # header fields
        action: str = None,  # e.g. 'alert','drop','log','pass','block','react','reject','rewrite'
        rule_type: str = None,  # 'traditional','service','file','file_id'
        protocol: str = None,  # 'ip','icmp','tcp','udp' or service names
        src_ip: str = None,  # Source IP address
        src_port: int = None,  # Source port number
        direction: str = None,  # '->','<>'
        dst_ip: str = None,  # Destination IP address
        dst_port: int = None,  # Destination port number
        # general options
        msg: str = None,  # Message string
        reference: list[
            tuple[str, str]
        ] = None,  # List of tuples [('url','example.com'),...]
        gid: int = None,  # Group ID
        sid: int = None,  # Snort ID
        rev: int = None,  # Revision number
        classtype: str = None,  # Classification type
        priority: int = None,  # Priority level
        metadata: dict[str, str] = None,  # Metadata dictionary with key-value pairs
        service_opt: list[str] = None,  # List of service options
        rem: str = None,  # Remarks
        file_meta: dict[
            str, str
        ] = None,  # File metadata dictionary with keys type, id, category, group, version
        # payload options
        content: list[
            dict[str, str]
        ] = None,  # List of dictionaries with payload options
        pcre: list[str] = None,  # List of PCRE strings
        regex: list[str] = None,  # List of regex strings
        bufferlen: int = None,  # Buffer length
        isdataat: bool = None,  # Boolean indicating if data is at a specific location
        dsize: int = None,  # Data size
        # non-payload and post-detect (examples)
        flow: list[str] = None,  # List of flow options
        ttl: int = None,  # Time-to-live value
        ipopts: list[str] = None,  # List of IP options
        fragoffset: int = None,  # Fragment offset
        fragbits: str = None,  # Fragment bits
        priority_bit: str = None,  # Priority bit
        dce: str = None,  # DCE/RPC options
        ssl_state: str = None,  # SSL state options
        # other options as needed
    ):
        """Build a Snort rule string from provided parameters."""
        # build header
        parts = []
        if action in (
            "alert",
            "drop",
            "log",
            "pass",
            "block",
            "react",
            "reject",
            "rewrite",
        ):
            parts.append(action)

        # service/file/file_id rules only need action and keyword
        if rule_type in ("service", "file", "file_id"):
            if rule_type == "traditional":
                pass
            else:
                parts.append(rule_type)
        else:
            for x in (protocol, src_ip, src_port):
                if not x:
                    raise ValueError("protocol, src_ip, src_port required")
                parts.append(x)
            parts.append(direction or "->")
            for x in (dst_ip, dst_port):
                if not x:
                    raise ValueError("dst_ip,dst_port required")
                parts.append(x)

        header = " ".join(parts)

        # build options
        opts = []

        def opt(name, val):
            if isinstance(val, list):
                for v in val:
                    opts.append(f"{name}:{v};")
            elif val is not None:
                opts.append(f"{name}:{val};")

        # general opts
        if msg:
            opts.append(f"msg:'{msg}';")
        if reference:
            for scheme, rid in reference:
                opts.append(f"reference:{scheme},{rid};")
        opt("gid", gid)
        opt("sid", sid)
        opt("rev", rev)
        if classtype:
            opts.append(f"classtype:{classtype};")
        opt("priority", priority)
        if metadata:
            pairs = [f"{k} {v}" for k, v in metadata.items()]
            opts.append(f"metadata:{','.join(pairs)};")
        if service_opt:
            opts.append(f"service:{','.join(service_opt)};")
        if rem:
            opts.append(f"rem:'{rem}';")
        if file_meta:
            fm = file_meta
            parts = [f"type {fm['type']}", f"id {fm['id']}"]
            for k in ("category", "group", "version"):
                if fm.get(k):
                    parts.append(f"{k} '{fm[k]}'")
            opts.append(f"file_meta:{','.join(parts)};")
        # payload opts example
        if content:
            for c in content:
                segs = [f"content:'{c['value']}'"]
                for m in (
                    "fast_pattern",
                    "nocase",
                    "offset",
                    "depth",
                    "distance",
                    "within",
                    "width",
                    "endian",
                ):
                    v = c.get(m)
                    if isinstance(v, bool) and v:
                        segs.append(m)
                    elif v not in (None, False):
                        segs.append(f"{m} {v}")
                opts.append(f"{','.join(segs)};")
        # pcre, regex examples
        if pcre:
            for r in pcre:
                opts.append(f"pcre:'{r}';")
        if regex:
            for r in regex:
                opts.append(f"regex:'{r}';")
        # non-payload example
        if flow:
            opts.append(f"flow:{','.join(flow)};")
        # compile rule
        body = "\n    ".join(opts)
        return f"{header} (\n    {body}\n)"

        #

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
    snorty.building_rule_block(domain, verbose=True)
    snorty.building_rule_block_icmp("10.45.0.3", verbose=True)
    snorty.building_rule_alert_icmp("10.45.0.3", verbose=True)
