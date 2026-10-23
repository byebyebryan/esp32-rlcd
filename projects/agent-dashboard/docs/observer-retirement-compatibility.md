# Observer write and active-only retirement compatibility

The dashboard runtime uses the working-set profile for ordinary reads and the
full profile for explicit diagnostics. Its loaded-user presentation remains
independent of the producer membership union. Observer write capability and the
standalone active-only profile are not dashboard runtime dependencies.

The selected immutable a8/a24 bundle and its public SDK lock remain independent
consumer artifacts. Qualify that exact consumer against replacement producers
before changing managed selection; do not edit the bundle or its manifest.

The former prepared-client benchmark and its active fixture used the retired
profile and an older device wire. They are historical evidence, available at
[the pre-retirement source](https://github.com/byebyebryan/esp32-rlcd/tree/aaeb32b23bd936f1aae88fa5e0c96b81f15691ab/projects/agent-dashboard/scripts/measure-prepared-client.py).
Their removal from current tooling does not rerun or expand earlier performance
acceptance. Current prepared/working-set/two-home tests own consumer regression
checks. No firmware or native provider change is part of this compatibility pass.
