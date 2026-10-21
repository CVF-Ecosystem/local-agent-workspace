"""Checker v2 candidate package (G-02-C2/S1, FOUNDATION_ONLY). Chỉ hằng literal, không logic / literals only, no logic.

Các giá trị này lặp lại literal của owner C1 (schema/policy v2) để loader so khớp; owner vẫn là nguồn định nghĩa.
These repeat the C1 owner literals so the loader can compare them; the C1 owners stay the definition.
"""
SCHEMA_ID = 'urn:law:cvf:control:2'
SCHEMA_VERSION = 'law.cvf.control/2'
POLICY_VERSION = 'law.cvf.routing/2'
EVALUATION_BASIS = 'COOPERATIVE_WORKFLOW'
BIND_VERSION = 'law.cvf.bind/2'
POLICY_STATUS = 'CANDIDATE_NOT_ACTIVE'
V1_SCHEMA_VERSION = 'law.cvf.control/1'

MAX_INPUT_BYTES = 8 * 1024 * 1024
MIN_JSONSCHEMA = (4, 18)
