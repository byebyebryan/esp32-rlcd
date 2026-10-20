# Synthetic Observer API-v4 fixture

`view.json` is vendored unchanged from the public Agent Observer working-set
source at commit
[`58b90e1a4a6b57e2c07d10856206908d2619af5b`](https://github.com/byebyebryan/agent-observer/blob/58b90e1a4a6b57e2c07d10856206908d2619af5b/tests/fixtures/service-v4/view.json).

SHA256: `f657b8847142bbf36084c12527d83d31919a71205b5c5ffc271a424cdf0770a5`

The integration test treats it as synthetic input, filters it to Codex records,
and edits a deep copy before seeding disposable `ServiceState` instances. It
does not start a provider or read any user's Observer data.
