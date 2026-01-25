from dotenv import load_dotenv
import random
import time
import string
import os
import sys
import mysql.connector
from openai import OpenAI
from pathlib import Path


# ====== CONFIGURAÇÃO DO AMBIENTE ======
dotenv_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=dotenv_path)

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("ERRO: variável OPENAI_API_KEY não encontrada no .env")

client = OpenAI(api_key=api_key)

def gera_chave():
   caracteres = string.ascii_letters + string.digits
   chave = ''.join(random.choice(caracteres) for _ in range (16)) 
   return chave


def digitar(resposta, delay=0.02):
    for char in resposta:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay + random.uniform(0, 0.001))
    print()


def salvar_conversa(conversa_id):
    try:
        conn = mysql.connector.connect(
            host = "localhost",
            user = "root",
            password = "F@miliamlln04",
            database = "IARA_IC"
        )
        cursor = conn.cursor()

        sql = "INSERT INTO conversa(conversa_id) values (%s)"
        valores = (conversa_id,)

        cursor.execute(sql,valores)
        conn.commit()

        cursor.close()
        conn.close()

        
    except mysql.connector.Error as err:
         print(f"\033[31m[ERRO]\033[0m Falha ao salvar no banco: {err}")


def  salvar_historico(pergunta_resposta_id, conversa_id, pergunta,resposta):
    try:
        conn = mysql.connector.connect(
            host = "localhost",
            user = "root",
            password = "F@miliamlln04",
            database = "IARA_IC"
        )
        cursor = conn.cursor()

        sql = "INSERT INTO historico_conversa (pergunta_resposta_id, conversa_id, pergunta, resposta) values (%s, %s, %s, %s)"
        valores = (pergunta_resposta_id,conversa_id, pergunta, resposta)

        cursor.execute(sql,valores)
        conn.commit()

        cursor.close()
        conn.close()

        
    except mysql.connector.Error as err:
        print(f"\033[31m[ERRO]\033[0m Falha ao salvar no banco: {err}")

    
# ====== FUNÇÃO PRINCIPAL ======
def main():
    print("IARA - Inteligência Artificial para o Raciocínio Algoritímico")
    print("\nDigite 'sair' para encerrar a conversa.\n")

    system_prompt = """
    Você é IARA, uma tutora virtual de programação em nível universitário.
    Seu papel é apoiar o aluno no desenvolvimento do raciocínio lógico e conceitual,
    promovendo autonomia intelectual e evitando a entrega de respostas prontas.

    Diretrizes pedagógicas:
    
    - Priorize explicações conceituais antes de qualquer orientação prática.
    - Estimule o pensamento crítico e a construção ativa do raciocínio.
    - Utilize perguntas orientadoras apenas após uma explicação conceitual inicial.
    - Faça no máximo uma pergunta por interação, baseada na resposta do aluno.
    - Ofereça dicas graduais, do mais abstrato ao mais concreto.
    - Evite fornecer soluções completas ou códigos finais.
    - Caso o aluno exija código, utilize apenas pseudocódigo ou fragmentos isolados.
    - É permitido explicar sintaxe, estruturas e comandos, desde que não componham uma solução fechada.
    - Incentive a experimentação, o teste de hipóteses e a depuração.
    - Mantenha um tom empático, claro e professoral.
    - Ao identificar um acerto, explique o motivo do sucesso.
    - Utilize exemplos criativos e situações do cotidiano.
    - Ao final de cada tema, proponha um pequeno exercício mental de reflexão.

    """
    messages = [
        {"role": "system", "content": system_prompt}
    ]
    
    # Vamo ver se aqui da certo de gerar uma chave só
    conversa_id = gera_chave()
    salvar_conversa(conversa_id)
    while True:
        user_input = input("\n\033[32mVocê: \033[0m")
        
        if user_input.lower() == "sair":
            
            break        
        #Limita o tamanho da message pra menos de 20 inputs do usuário
        messages.append({"role": "user", "content": user_input})
        
        if len(messages) > 20:
            messages = [messages[0]] + messages[-10:]

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.6,
            max_tokens=1000
        )

        resposta = completion.choices[0].message.content.strip()
        pergunta_resposta_id = gera_chave()
        salvar_historico(pergunta_resposta_id, conversa_id, user_input, resposta)

        print("\n\033[31mIARA: \033[0m", end="")
        digitar(resposta, delay=0.015)

        messages.append({"role": "assistant", "content": resposta})
        

if __name__ == "__main__":
    main()
    digitar("\n\033[31mIARA:\033[0m Obrigada pela sessão, até mais!\n", delay=0.015)

