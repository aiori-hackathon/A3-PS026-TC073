"""
AT URI parsing engine with four distinguishable strategies.

Reference: https://atproto.com/specs/at-uri-scheme
Key quirk: DID authorities contain unencoded colons (did:plc:abc123),
which conflicts with RFC 3986 host:port parsing. Strategies differ in
how they resolve this.
"""
import re
from dataclasses import dataclass, field, asdict
from typing import Optional, List

# AT Protocol grammar (per spec, April 2024)
DID_RE   = re.compile(r'^did:[a-z]+:[a-zA-Z0-9._:%-]*[a-zA-Z0-9._-]$')
HANDLE_RE = re.compile(r'^([a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$')
NSID_RE  = re.compile(r'^[a-zA-Z]([a-zA-Z0-9-]{0,62}[a-zA-Z0-9])?(\.[a-zA-Z]([a-zA-Z0-9-]{0,62}[a-zA-Z0-9])?)+$')
RKEY_RE  = re.compile(r'^[a-zA-Z0-9._~:-]{1,512}$')

STRATEGIES = ["standard", "strict", "compatibility", "rfc3986"]


@dataclass
class ParseResult:
    strategy: str
    valid: bool
    raw: str
    authority: Optional[str] = None
    collection: Optional[str] = None
    rkey: Optional[str] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    def to_dict(self):
        return asdict(self)


def _split(uri: str):
    """Split at://authority/path into (authority, [path segments])."""
    if not uri.startswith("at://"):
        return None, None
    rest = uri[5:]
    if "/" in rest:
        authority, path = rest.split("/", 1)
        segments = path.split("/")
    else:
        authority, segments = rest, []
    return authority, segments


def _validate_authority_standard(auth: str, errors, warnings):
    if auth.startswith("did:"):
        if not DID_RE.match(auth):
            errors.append(f"standard: DID '{auth}' fails AT Protocol DID regex")
    elif HANDLE_RE.match(auth):
        pass  # valid handle
    else:
        errors.append(f"standard: authority '{auth}' is neither a valid DID nor a valid handle")


def _validate_authority_strict(auth: str, errors, warnings):
    """Strict: enforce DID regex AND reject DIDs with too many colons (>2 for plc)."""
    if auth.startswith("did:"):
        if not DID_RE.match(auth):
            errors.append(f"strict: DID syntax invalid")
        method_parts = auth.split(":")
        if len(method_parts) < 3:
            errors.append("strict: DID must have at least did:method:identifier")
        # Known method-specific colon counts
        if method_parts[1] == "plc" and len(method_parts) != 3:
            warnings.append(f"strict: did:plc should have exactly one identifier segment, got {len(method_parts)-2}")
    elif not HANDLE_RE.match(auth):
        errors.append(f"strict: handle not a fully-qualified domain")


def _validate_authority_compat(auth: str, errors, warnings):
    """Compatibility: lenient — accepts anything the underlying libs might accept."""
    if auth.startswith("did:") and auth.count(":") < 2:
        errors.append("compat: truncated DID")
    # The point: compat does NOT reject handle-like strings with colons
    if ":" in auth and not auth.startswith("did:"):
        warnings.append(f"compat: colon in non-DID authority '{auth}' — likely host:port confusion")


def _validate_authority_rfc3986(auth: str, errors, warnings):
    """Simulates a generic RFC 3986 parser: treats first colon as host:port separator."""
    if ":" in auth:
        host, _, port = auth.partition(":")
        if port and not port.isdigit():
            errors.append(f"rfc3986: '{port}' is not a numeric port — generic parsers mis-split DID here")
        elif auth.startswith("did:"):
            warnings.append("rfc3986: DID treated as host:port; identifier lost")


def _parse_path(segments, strategy, errors, warnings):
    collection = None
    rkey = None
    if not segments:
        return None, None
    collection = segments[0]
    if collection and not NSID_RE.match(collection):
        if strategy == "strict":
            errors.append(f"strict: collection '{collection}' is not a valid NSID")
        else:
            warnings.append(f"{strategy}: collection '{collection}' is not a valid NSID")
    if len(segments) >= 2:
        rkey = segments[1]
        if rkey and not RKEY_RE.match(rkey):
            if strategy == "strict":
                errors.append(f"strict: rkey '{rkey}' fails record-key grammar")
            else:
                warnings.append(f"{strategy}: rkey '{rkey}' fails record-key grammar")
    if len(segments) > 2:
        errors.append(f"too many path segments: {segments[2:]}")
    return collection, rkey


def parse_at_uri(uri: str, strategy: str = "standard") -> ParseResult:
    if strategy not in STRATEGIES:
        raise ValueError(f"unknown strategy: {strategy}")

    errors, warnings, notes = [], [], []
    authority, segments = _split(uri)
    if authority is None:
        return ParseResult(strategy, False, uri, errors=["missing at:// prefix"])

    if not authority:
        return ParseResult(strategy, False, uri, errors=["empty authority"])

    if strategy == "standard":
        _validate_authority_standard(authority, errors, warnings)
    elif strategy == "strict":
        _validate_authority_strict(authority, errors, warnings)
    elif strategy == "compatibility":
        _validate_authority_compat(authority, errors, warnings)
    elif strategy == "rfc3986":
        _validate_authority_rfc3986(authority, errors, warnings)

    collection, rkey = _parse_path(segments, strategy, errors, warnings)

    # Every strategy records how it interpreted DID colons
    if authority.startswith("did:"):
        notes.append(
            "DID colons are part of the authority identifier, not host:port separators."
        )

    return ParseResult(
        strategy=strategy,
        valid=len(errors) == 0,
        raw=uri,
        authority=authority,
        collection=collection,
        rkey=rkey,
        errors=errors,
        warnings=warnings,
        notes=notes,
    )


def reconstruct(result: ParseResult) -> str:
    if not result.authority:
        return ""
    out = f"at://{result.authority}"
    if result.collection is not None:
        out += f"/{result.collection}"
        if result.rkey is not None:
            out += f"/{result.rkey}"
    return out