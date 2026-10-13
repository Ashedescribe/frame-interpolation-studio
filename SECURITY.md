# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.4.x   | yes       |
| 0.3.x   | yes       |
| < 0.3   | no        |

## Reporting a vulnerability

Frame-interpolation-studio decodes untrusted media and loads model
weights from disk. Both are attack surfaces. If you find an issue,
email `security@frame-interpolation-studio.dev` with:

- A short description and impact.
- Steps to reproduce, or a minimal clip / weight file.
- Your Python version, OS build, and GPU driver.

We aim to acknowledge within 72 hours and ship a fix within 30 days
for high-severity issues.

## Scope

In scope:
- Memory corruption or RCE in native decoders (FFmpeg, PyAV).
- Path traversal in the batch pipeline when resolving output dirs.
- Unsafe deserialization of `.pth` / `.onnx` / `.engine` weights.
- Arbitrary code execution via the plugin hook in
  `src/fis/services/plugin_host.py`.

Out of scope:
- Denial of service from absurdly large input clips on a machine with
  insufficient RAM. That is expected; we document limits in the README.
- Issues that require the attacker to already control the user's
  Python environment.

## Hardening notes for users

- Run the tool against media you trust.
- Only load weights from the official mirror or a hash you verified.
- The plugin host runs with the same privileges as the app. Treat a
  plugin like any other executable.