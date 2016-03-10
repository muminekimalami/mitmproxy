"""
This module handles the import of mitmproxy flows generated by old versions.
"""
from __future__ import absolute_import, print_function, division
from . import version


def convert_013_014(data):
    data["request"]["first_line_format"] = data["request"].pop("form_in")
    data["request"]["http_version"] = "HTTP/" + ".".join(str(x) for x in data["request"].pop("httpversion"))
    data["response"]["status_code"] = data["response"].pop("code")
    data["response"]["body"] = data["response"].pop("content")
    data["server_conn"].pop("state")
    data["server_conn"]["via"] = None
    data["version"] = (0, 14)
    return data


def convert_014_015(data):
    data["version"] = (0, 15)
    return data


def convert_015_016(data):
    for m in ("request", "response"):
        if "body" in data[m]:
            data[m]["content"] = data[m].pop("body")
        if "httpversion" in data[m]:
            data[m]["http_version"] = data[m].pop("httpversion")
    if "msg" in data["response"]:
        data["response"]["reason"] = data["response"].pop("msg")
    data["request"].pop("form_out", None)
    data["version"] = (0, 16)
    return data


def convert_016_017(data):
    data["server_conn"]["sock_address"] = None
    data["version"] = (0, 17)
    return data


converters = {
    (0, 13): convert_013_014,
    (0, 14): convert_014_015,
    (0, 15): convert_015_016,
    (0, 16): convert_016_017,
}


def migrate_flow(flow_data):
    while True:
        flow_version = tuple(flow_data["version"][:2])
        if flow_version == version.IVERSION[:2]:
            break
        elif flow_version in converters:
            flow_data = converters[flow_version](flow_data)
        else:
            v = ".".join(str(i) for i in flow_data["version"])
            raise ValueError("Incompatible serialized data version: {}".format(v))
    return flow_data
