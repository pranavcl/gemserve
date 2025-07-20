# GemServe

GemServe is a simple [Gemini](https://geminiprotocol.net) protocol server to serve `.gmi` files. Written in [Python](https://python.org/) and compiled with [PyInstaller](https://pyinstaller.org/en/stable/).

**Ideal for beginners** or capsules that don't require server-side scripting - **Just download the binary executable and run it**, and start editing `.gmi` files in the `/docs/` folder. `index.gmi` is served on the root endpoint.

## Quickstart

1. Click on the `bin/` folder above and download the executable for your OS.

- gemserve_win64.exe (For 64-bit Windows)
- gemserve_linux_x86_64 (For 64-bit Linux)

More binaries coming soon

2. Create a folder for your gemini capsule (eg. `mywebsite/`) and copy the executable inside it.
3. Run the executable and point your Gemini client to `gemini://localhost`. You will have to create an exception (Ctrl+Shift+U in Lagrange) for the self-signed certificate.
4. Start editing files in `/docs/`

## Compiling from Source

### Dependencies

1. Install [Python](https://python.org/) on your system.

### Instructions

1. First, clone the repository:

```bash
git clone https://github.com/pranavcl/gemserve
```

2. Enter the cloned directory and run `pip install -r requirements.txt`:

```bash
cd gemserve
pip install -r requirements.txt
```

3. Run the app using `python`:

```
python run.py
```

**All done!**

## License

Published under the [GNU GPLv3 License](https://www.gnu.org/licenses/gpl-3.0.en.html)