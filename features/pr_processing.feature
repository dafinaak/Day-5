Feature: IPRMS deterministic purchase requisition processing
  As a procurement system
  I want to process PR bundles through a deterministic 8-agent pipeline
  So that the same input bundle and configs always produce the same PO draft or exception route

  Background:
    Given the IPRMS pipeline is configured with policy_pack.yaml, routing_rules.json and tolerance_settings.json
    And the pipeline runs agents A through H deterministically

  Scenario: Clean PR is converted into PO draft
    Given a PR bundle with a valid manifest and well-formed line items
    And the requested amount is within the approved budget
    And every line item matches a preferred vendor
    And no policy, bid-threshold, sole-source or split-order rule is triggered
    When the pipeline processes the PR bundle
    Then the PR is auto-approved
    And a PO draft is generated
    And audit artifacts (audit_log, evidence_index, metrics) are written

  Scenario: PR exceeds budget
    Given a PR bundle with a valid manifest and well-formed line items
    And the requested amount exceeds the approved budget beyond tolerance_settings.json limits
    When the pipeline processes the PR bundle
    Then Agent C flags a budget validation failure
    And no PO draft is auto-generated
    And the PR is routed to FP&A review per routing_rules.json
    And the budget exception is recorded in the audit_log

  Scenario: PR uses non-preferred vendor
    Given a PR bundle with a valid manifest and well-formed line items
    And at least one line item references a vendor that is not on the preferred vendor list
    When the pipeline processes the PR bundle
    Then Agent D flags a non-preferred vendor match
    And the PR is routed to Procurement review per routing_rules.json
    And the vendor exception is recorded in the audit_log

  Scenario: Split-order anomaly is detected
    Given a PR bundle containing multiple requisitions to the same vendor
    And the requisitions appear to be split to stay under a bid or approval threshold
    When the pipeline processes the PR bundle
    Then Agent G detects a split-order anomaly
    And no PO draft is auto-generated
    And the PR is routed to Procurement review per routing_rules.json
    And the anomaly is recorded in the audit_log

  Scenario: Sole-source PR requires compliance review
    Given a PR bundle that is declared as sole-source above the bid threshold
    And no competitive bids are present in the bundle
    When the pipeline processes the PR bundle
    Then Agent F flags the sole-source / bid-threshold condition
    And Agent E confirms a policy compliance gate is required
    And the PR is routed to Legal and Procurement compliance review per routing_rules.json
    And the sole-source justification requirement is recorded in the audit_log
