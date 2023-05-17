# Wirebind

**Wirebind is currently an early preview!** Don't use it for production things, but feel free to poke around, and open issues if you find bugs or have ideas.

[![Javascript Tests](https://github.com/drifting-in-space/wirebind/actions/workflows/javascript.yml/badge.svg)](https://github.com/drifting-in-space/wirebind/actions/workflows/javascript.yml) [![Python Tests](https://github.com/drifting-in-space/wirebind/actions/workflows/python.yml/badge.svg)](https://github.com/drifting-in-space/wirebind/actions/workflows/python.yml)

Wirebind is a reactive data binding library built on top of WebSockets. With Wirebind, your application can interact with state as if it were local and have it seamlessly synchronized across the network.

Wirebind is a language-agnostic protocol built as an extension of CBOR ([RFC 8949](https://datatracker.ietf.org/doc/html/rfc8949)). It is language-agnostic. Currently, libraries exist for Python and JavaScript.

## Demo

This demo (located in `/demos/stable-diffusion`) shows a Stable Diffusion interface built with Wirebind. Wirebind makes it easy to stream back progress snapshots, and to change weights _even while inference is running_.

https://github.com/drifting-in-space/wirebind/assets/46173/208acf23-da15-4e19-a461-bcd603c42cc6

