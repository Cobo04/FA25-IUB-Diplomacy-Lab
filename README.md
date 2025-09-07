# 🛰 FA25-IUB-Diplomacy-Lab
Quantitative analysis on the Chinese Space Industrial Complex

## ⚡ Quickstart

### WSL

Clone the repository:

```bash
git clone https://github.com/Cobo04/FA25-IUB-Diplomacy-Lab.git
```

```bash
cd FA25-IUB-Diplomacy-Lab
```

Create a `venv` environment, activate it, and install dependencies with `pip`:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Check that `flask` runs without errors:

```bash
python -m flask --version
```

### PowerShell + Windows

<details>
<summary>Create a venv environment, activate it, and install requirements.</summary>

> ```powershell
> python -m venv venv
> .\venv\Scripts\Activate.ps1
> pip install -r requirements.txt
> ```

</details>

<details>
<summary><strong>Execution Policy</strong>: FOR AN ERROR</summary>

> Execution policies can throw errors. This should only need to be done once then immediately reverted:
>
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

</details>

Check that `flask` runs without errors:

```bash
python -m flask --version
```

## 🚀 Start The server

Make sure your environment is activated. You should see a `(venv)` in the terminal if it is:

```bash
source venv/bin/activate
```

OR

```bash
.\venv\Scripts\Activate.ps1
```

Running the package as a module will open the development server on http://localhost:5000

```bash
python -m flaskapp
```

## 📝 Relevant Information

### Nothing here quite yet!