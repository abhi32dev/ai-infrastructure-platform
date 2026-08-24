import os
import json
import re

VAULT_PATH = os.path.join(os.path.dirname(__file__), "..", "resume_vault", "profile_vault.json")

def load_vault():
    if os.path.exists(VAULT_PATH):
        with open(VAULT_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def solve_form_field(telemetry_data):
    """
    Intelligently analyzes stuck form fields or custom disclaimers and provides real-time resolution instructions!
    """
    field_label = (telemetry_data.get("field_name") or "").lower()
    dom_snippet = (telemetry_data.get("dom_snapshot") or "").lower()
    disclaimer = (telemetry_data.get("disclaimer_text") or "").lower()

    vault = load_vault()
    pers = vault.get("personal", {})
    auth = vault.get("work_authorization", {})
    eeo = vault.get("eeo", {})
    pref = vault.get("preferences", {})

    # 1. Salary Expectation Questions
    if any(k in field_label or k in dom_snippet for k in ["salary", "compensation", "desired pay", "pay expectation"]):
        return {
            "status": "resolved",
            "action": "fill_input",
            "value": "$180,000",
            "reason": "Resolved from profile salary preference"
        }

    # 2. How did you hear about us / Source Questions
    if any(k in field_label or k in dom_snippet for k in ["hear about", "how did you find", "source", "referral"]):
        return {
            "status": "resolved",
            "action": "fill_input",
            "value": "LinkedIn / Company Website",
            "reason": "Resolved standard source attribution"
        }

    # 3. Work Authorization & Sponsorship Questions
    if any(k in field_label or k in dom_snippet for k in ["authorized to work", "work authorization", "legally authorized"]):
        return {
            "status": "resolved",
            "action": "select_radio",
            "value": auth.get("legallyAuthorizedUS", "Yes"),
            "reason": "Resolved US Work Authorization = Yes"
        }

    if any(k in field_label or k in dom_snippet for k in ["sponsorship", "visa", "require sponsorship"]):
        return {
            "status": "resolved",
            "action": "select_radio",
            "value": auth.get("requireSponsorship", "Yes"),
            "reason": "Resolved Visa Sponsorship = Yes"
        }

    # 4. Years of Experience Questions
    if any(k in field_label or k in dom_snippet for k in ["years of experience", "how many years", "experience with"]):
        return {
            "status": "resolved",
            "action": "fill_input",
            "value": "8",
            "reason": "Resolved senior engineering experience"
        }

    # 5. Hybrid / Relocation Questions
    if any(k in field_label or k in dom_snippet for k in ["relocate", "relocation", "hybrid", "onsite"]):
        return {
            "status": "resolved",
            "action": "select_radio",
            "value": "Yes",
            "reason": "Resolved hybrid office willingness"
        }

    # 6. EEO Gender / Race / Veteran
    if "gender" in field_label:
        return {"status": "resolved", "action": "select_dropdown", "value": eeo.get("gender", "Male")}
    if "race" in field_label or "ethnicity" in field_label:
        return {"status": "resolved", "action": "select_dropdown", "value": eeo.get("race", "Asian (Not Hispanic or Latino)")}
    if "veteran" in field_label:
        return {"status": "resolved", "action": "select_dropdown", "value": eeo.get("veteran", "I am not a veteran")}
    if "disability" in field_label:
        return {"status": "resolved", "action": "select_dropdown", "value": eeo.get("disability", "No, I do not have a disability")}

    # 7. Default Safe Fallback
    return {
        "status": "fallback",
        "action": "fill_input",
        "value": pers.get("fullName", "Abhishek Singh"),
        "reason": "Default fallback to master profile details"
    }
