"""Checker v3 candidate package (G-02-C2/S3-C/D, BINDING_ROUTING_ONLY). Chỉ hằng literal, không logic / literals only, no logic.

Các giá trị này lặp lại literal của owner v3 (schema/policy) để loader so khớp; owner vẫn là nguồn định nghĩa.
These repeat the v3 owner literals so the loader can compare them; the v3 owners stay the definition.
"""
SCHEMA_ID = 'urn:law:cvf:control:3'
SCHEMA_VERSION = 'law.cvf.control/3'
POLICY_VERSION = 'law.cvf.routing/3'
EVALUATION_BASIS = 'COOPERATIVE_WORKFLOW'
BIND_VERSION = 'law.cvf.bind/3'
POLICY_STATUS = 'CANDIDATE_NOT_ACTIVE'
V1_SCHEMA_VERSION = 'law.cvf.control/1'
V2_SCHEMA_VERSION = 'law.cvf.control/2'  # chỉ để gợi ý chẩn đoán, không bao giờ được chấp nhận / diagnostic hint only, never accepted

MAX_INPUT_BYTES = 8 * 1024 * 1024
MIN_JSONSCHEMA = (4, 18)
