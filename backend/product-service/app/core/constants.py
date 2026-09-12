"""
Application-wide constants.

UserRole values are placeholders until Amazon Cognito is configured.
Once Cognito User Pool Groups are created, the group names must match
these enum values *exactly* (case-sensitive) — a mismatch here is a
silent failure: role checks like `if reviewer_role != UserRole.DATA_STEWARD`
will just quietly always be False instead of raising an error.

TODO: when Cognito is set up, either:
  (a) name the Cognito Groups exactly "Customer", "Supplier", "DataSteward", or
  (b) update these enum values to match whatever group names you actually create.
Whichever direction you choose, keep this file as the single source of truth
and never hardcode a role string anywhere else in the codebase.
"""

import enum


class UserRole(str, enum.Enum):
    CUSTOMER = "Customer"
    SUPPLIER = "Supplier"
    DATA_STEWARD = "DataSteward"