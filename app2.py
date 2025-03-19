import tkinter as tk
from tkinter import filedialog, messagebox
import requests
import base64
import os

# Variáveis globais
token = ""
owner = ""
repo = ""
branch = "main"  # Fixo

def carregar_configuracoes():
    global token, owner, repo
    if not os.path.exists("config.txt"):
        messagebox.showerror("Erro", "Arquivo config.txt não encontrado.")
        return

    with open("config.txt", "r") as f:
        linhas = f.readlines()
        for linha in linhas:
            if linha.startswith("token="):
                token = linha.strip().split("=", 1)[1]
            elif linha.startswith("usuario="):
                owner = linha.strip().split("=", 1)[1]
            elif linha.startswith("repositorio="):
                repo = linha.strip().split("=", 1)[1]

def enviar_arquivo():
    global token, owner, repo, branch
    local_file_path = entry_local_file.get()

    if not os.path.isfile(local_file_path):
        messagebox.showerror("Erro", "Arquivo local não encontrado.")
        return

    repo_file_name = os.path.basename(local_file_path)  # Nome do arquivo no repo
    with open(local_file_path, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf-8")

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{repo_file_name}"
    data = {
        "message": f"Upload de {repo_file_name} via app",
        "content": content,
        "branch": branch
    }

    response = requests.put(url, headers=headers, json=data)

    if response.status_code in [200, 201]:
        messagebox.showinfo("Sucesso", f"{repo_file_name} enviado com sucesso.")
    else:
        messagebox.showerror("Erro", f"Erro ao enviar: {response.text}")

def deletar_arquivo():
    global token, owner, repo, branch
    local_file_path = entry_local_file.get()

    if not os.path.isfile(local_file_path):
        messagebox.showerror("Erro", "Arquivo local não encontrado.")
        return

    repo_file_name = os.path.basename(local_file_path)

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    url_get = f"https://api.github.com/repos/{owner}/{repo}/contents/{repo_file_name}?ref={branch}"
    response_get = requests.get(url_get, headers=headers)

    if response_get.status_code == 200:
        sha = response_get.json()["sha"]
    else:
        messagebox.showerror("Erro", f"Erro ao obter SHA: {response_get.text}")
        return

    url_delete = f"https://api.github.com/repos/{owner}/{repo}/contents/{repo_file_name}"
    data = {
        "message": f"Deletando {repo_file_name} via app",
        "sha": sha,
        "branch": branch
    }

    response_delete = requests.delete(url_delete, headers=headers, json=data)

    if response_delete.status_code == 200:
        messagebox.showinfo("Sucesso", f"{repo_file_name} deletado com sucesso.")
    else:
        messagebox.showerror("Erro", f"Erro ao deletar: {response_delete.text}")

def selecionar_arquivo():
    file_path = filedialog.askopenfilename()
    if file_path:
        entry_local_file.delete(0, tk.END)
        entry_local_file.insert(0, file_path)

# Interface
root = tk.Tk()
root.title("GitHub - Enviar / Deletar Arquivo")

tk.Label(root, text="Arquivo Local:").grid(row=0, column=0, sticky="e")
entry_local_file = tk.Entry(root, width=50)
entry_local_file.grid(row=0, column=1)

btn_browse = tk.Button(root, text="Selecionar Arquivo", command=selecionar_arquivo)
btn_browse.grid(row=0, column=2)

btn_upload = tk.Button(root, text="Enviar Arquivo", command=enviar_arquivo, bg="green", fg="white")
btn_upload.grid(row=1, column=0, pady=10)

btn_delete = tk.Button(root, text="Deletar Arquivo", command=deletar_arquivo, bg="red", fg="white")
btn_delete.grid(row=1, column=1, pady=10)

# Carregar configurações ao iniciar
carregar_configuracoes()

root.mainloop()
