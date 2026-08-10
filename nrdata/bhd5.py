"""Encrypted archive header (BHD5) handling for the data*.bhd/bdt pairs.

The header is "decrypted" with a public RSA key: raw modular exponentiation
over 256-byte blocks, each yielding 255 bytes of plaintext.
"""

from __future__ import annotations

from Crypto.PublicKey import RSA

BLOCK_IN = 256
BLOCK_OUT = 255

# Per-archive public keys for Nightreign. Elden Ring's keys do not work here;
# this was verified against the actual files.
ARCHIVE_KEYS = {
    "data0": """-----BEGIN RSA PUBLIC KEY-----
MIIBDAKCAQEAz8F9U1V9hgKs40gdzl1ZOf3IBirf6xUEzXtDd6oSEBE6XiYocvAB
ykiK+WMdAaJL7HJ58Gt2xSRxA3t9toCGKMI/3gNAfcR0BV83gsQo0O0dVP0fqyxX
lA2pGN5B4IE8aLWPX2cNNFSFKAdjYnzsYSevzef/pgnpV1ZgPf2j2SQwNGSufYeN
3Owji8l0K2C0fKIx6gSO0cK9kvTIm8AdpvzZbBkTylT1jF3m8DsSA1OFzFJTdFyZ
bTRi85M6bmv6rHtvZc5OW21dye7Q6fmLlxOyMetLTu4dpOXjHAAf/LFTbfQpXFr9
aXO4O6I7nWDJn7FRzNlLkb8RwSyZ1/KWyQIFALEDsAc=
-----END RSA PUBLIC KEY-----""",
    "data1": """-----BEGIN RSA PUBLIC KEY-----
MIIBDAKCAQEA0E6dtnDmT6d2+VaNkPzomUNv+T6896H//RAaTR2guPACMDNZpAsF
vV3MfNcR2BS6Cbxl55MmMWsmsZs1s293MuOdS+c99vmZbNYcXWjx0uJGO+VrRXe4
3TRzmQFh1uD+Xcq6+wYfTrGyLOdAtmwdDXNvW8jYoFDM7nsuoPKOXKtKd0uz7/MK
ZYLk1J7pAoBQqw9VD5qi2Ih86zn0VWm5lLMTI0qnutOzpZVDvZWBg/jr4Nbnr/Ox
PLeJO1tFuRuHUPuBAWtYM/J23MPqqKkQrG5z2r7PexUI744UPdmo3Sn+Mqynuxxv
V9SEhska6pStzn8R9i94wOKPTQ32HEFuUQIFAP////8=
-----END RSA PUBLIC KEY-----""",
    "data2": """-----BEGIN RSA PUBLIC KEY-----
MIIBDAKCAQEAqpkf9yHnx8k84+WXITLFUW/STypXjZMPuw842pzNHa5L7v9gU4M5
hBHwTQs0YIcfnf+mbjqoJYnmYPBblxLjFXgwT4ICJdpnPMY75BwD0Nv28/CvvIsA
0QQWOhUeOXnm5BT26dGYi3CHHPvD14F76tJt3TO/CC3fyhdxne9Cra5G87aGTJGv
0ImsU0KPCizYX/RHQ2jdJdlB5BHzkMgLhIaEdhC3nhIqMJDNQNGKMo7rRV1tAEGf
0zIZ23PGEsPsbVg31nnnRoq338WfD9ArZZG6bM11vlfVcYmrJs7v4vBjKXnYVwVX
0rQGIfSNDnaZcEj4tsl04AqnupTdvSrHXwIFANOg6RU=
-----END RSA PUBLIC KEY-----""",
    # Recovered from nightreign.exe (all six archive keys are stored there as
    # plaintext PEM). Community key lists omit this one; verified by decrypting
    # dlc01.bhd to the BHD5 magic.
    "dlc01": """-----BEGIN RSA PUBLIC KEY-----
MIIBDAKCAQEA1q4MOehlD++h5Ietq9Jk97eGOJL2zDpDcu9Wk6RXK1+R3LycMBQl
L/hnPg/qqvcoViA7wLX5GOFr5lo6dtKaQqlBkBqgYHGIdBvioBPZ8BuXAjYr3sm8
N0SYC2TNHXmfw6yFC+ePsrl+gNldrO//XXY27hsGgcegfWr6JuQaJti/BOKlGb8A
RbKwyIqGc5WiWj/v0tGE1cdPi0fLQRbTrLFaQtx1roQVqsQuJ5zRGTpnj/mhaJtq
J7V0s5gLG5CCevx71lN8m7oyWk2JemzSLvllwv4tjtzrw3jNQtiYb8nzy2Spjibs
vX1iRCg5btMSiNPcSeIJ5jX+FUW9LSnrkwIFAKhopbM=
-----END RSA PUBLIC KEY-----""",
    "data3": """-----BEGIN RSA PUBLIC KEY-----
MIIBCwKCAQEAwm2Rcw4eoP8FgWijxw1X8b9rEVFsVqy7rXWcH2yVm61yYBlzPlTq
Kqnc2VeqZSh/TLXeFY3+Om2X78RQxZNS3L3OokvD7l/0wqPIpXSSumeeL8UAZm5k
7nFA2m2HJfc+F07kNwwCEqhmFs5YQIMnWyIrqnEax/qSncFErLjIYMBMArVnVLE8
WqgsD7N8lW937dlUcT2TaPh1HfjavKOSUy/OHM9zaneyDL4NRmDdU8GmNXTSm5kP
YoSRCDIvFVj0g5iaXr60eRh0d+40TctoBUdtaoJCPOyRlmkE7qU6Q9FyyvMNbhtf
D95d+6IJejNd7kvyV/ISlB37kb2Uh9TavwIEOqKLtw==
-----END RSA PUBLIC KEY-----""",
}


def decrypt_header(data: bytes, pem: str) -> bytes:
    key = RSA.import_key(pem)
    n, e = key.n, key.e

    out = bytearray()
    for start in range(0, len(data) - BLOCK_IN + 1, BLOCK_IN):
        block = int.from_bytes(data[start : start + BLOCK_IN], "big")
        plain = pow(block, e, n).to_bytes(BLOCK_IN, "big")
        out += plain[1:]  # drop the leading padding byte
    return bytes(out)


def path_hash(path: str) -> int:
    """FromSoftware's 64-bit archive path hash (prime 0x85)."""
    normalised = path.strip().replace("\\", "/").lower()
    if not normalised.startswith("/"):
        normalised = "/" + normalised
    h = 0
    for ch in normalised:
        h = (h * 0x85 + ord(ch)) & 0xFFFFFFFFFFFFFFFF
    return h
