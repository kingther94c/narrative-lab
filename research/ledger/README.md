# Sealed ledger

Hash manifests of forecasts that were sealed before their outcomes existed. The forecasts
themselves, and the inputs they were made from, are stored outside git.

A manifest is a JSON Lines file, one line per sealed item:

```
{"experiment": "EXP-0001", "item_id": "...", "model": "<repo@revision or model id>",
 "input_sha256": "...", "forecast_sha256": "...", "sealed_at": "YYYY-MM-DDTHH:MM:SSZ"}
```

The commit that adds a manifest is the timestamp. An outcome is opened only after its manifest is
committed, and the reveal is recorded in the experiment's verdict.

Nothing is sealed yet.
