# Operations, SLOs and Cost

## Recommended SLIs

- Realtime connection success and time to first audio
- Completed useful turns / started turns
- VAD overlap, silence and interruption success
- Transcript finalization and partial-turn rate
- Evaluation latency and scoring failure rate
- Session completion and deletion success
- Redaction and prompt-injection event rates
- Cost per completed interview and reserved-versus-actual usage
- Score distribution and deterministic/judge disagreement drift

## SLO examples

- 99.5% of admitted offline turns remain usable.
- 99% of successful realtime negotiations produce first audio within the regional target.
- 99.9% of committed answers are returned idempotently after retry in the production store.
- 100% of deletion requests complete across primary and derived artifacts within policy.

## Runbook order

1. Separate client microphone/browser failures from SDP/provider failures.
2. Preserve the active turn and offer typed/browser-dictation fallback.
3. Stop admission before retry amplification or cost exhaustion.
4. Inspect correlated metrics/events without opening transcript content.
5. Roll back prompt/model/rubric versions independently.
6. Reconcile provider usage, quota leases and partial session artifacts.
