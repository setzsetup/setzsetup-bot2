import os
import time
import requests
import asyncio
import random
from datetime import datetime
from bs4 import BeautifulSoup
from telegram import Bot

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
bot = Bot(token=BOT_TOKEN)

frases = [
    "🔥 Oferta do dia!",
    "🚨 Corre que é por tempo limitado!",
    "💥 Achado gamer que vale o clique!",
    "🎯 Preço top que a gente garimpou!",
    "🎮 Item essencial pra setup top!",
    "⭐ A galera tá levando esse agora!",
    "🧠 Upgrade certeiro pro seu setup!",
    "🏆 Top escolha dos gamers brasileiros!",
    "🤑 Economize agora com esse achado!",
    "📦 Oferta imperdível em estoque!"
]

palavras_chave = [
    "monitor gamer", "notebook gamer", "cadeira gamer", "teclado mecânico", "mouse gamer", "headset gamer",
    "mesa gamer", "kit gamer", "gabinete gamer", "controle gamer", "mousepad gamer", "webcam gamer",
    "pc gamer", "setup gamer", "placa de vídeo", "ssd", "memória ram ddr4", "fonte modular",
    "water cooler", "cooler rgb", "placa mãe gamer", "hub usb", "monitor 144hz", "switch hdmi",
    "base notebook", "teclado low profile", "microfone gamer", "light ring", "cadeira ergonômica"
]

rodada = 1

async def buscar_uma_oferta(termo):
    print(f"🔍 Buscando por: {termo}")
    query = termo.replace(" ", "+")
    url = f"https://www.amazon.com.br/s?k={query}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')

        itens = soup.select("div.s-result-item")
        random.shuffle(itens)

        for item in itens:
            img_tag = item.select_one("img")
            link_tag = item.select_one("a.a-link-normal")
            preco_whole = item.select_one("span.a-price-whole")
            preco_fraction = item.select_one("span.a-price-fraction")

            if (
                img_tag and link_tag and '/dp/' in link_tag['href']
                and preco_whole and preco_fraction
            ):
                titulo = img_tag.get('alt', '').strip()
                imagem = img_tag.get('src', '')
                link_base = "https://www.amazon.com.br" + link_tag['href'].split("?")[0]
                link_afiliado = link_base + "?tag=setzsetup-20"

                preco_limpo = preco_whole.text.replace(",", "").strip()
                preco = f"R$ {preco_limpo},{preco_fraction.text.strip()}"

                if titulo and imagem:
                    print(f"✅ Oferta encontrada: {titulo[:60]}... | {preco}")
                    return {
                        "titulo": titulo,
                        "imagem": imagem,
                        "link": link_afiliado,
                        "preco": preco
                    }

        print(f"❌ Nenhuma oferta com preço disponível para '{termo}'")
        return None

    except Exception as e:
        print(f"⚠️ Erro com '{termo}': {e}")
        return None

async def enviar_ofertas():
    global rodada
    while True:
        agora = datetime.now().strftime("%d/%m/%Y")
        print("\n──────────────────────────────")
        print(f"📦 Rodada #{rodada} — {agora}")
        print("🔄 Iniciando nova busca de ofertas...")

        tentativas = palavras_chave.copy()
        random.shuffle(tentativas)

        ofertas = []

        for termo in tentativas:
            if len(ofertas) >= 2:
                break
            oferta = await buscar_uma_oferta(termo)
            if oferta:
                ofertas.append(oferta)
            await asyncio.sleep(2)

        if ofertas:
            for oferta in ofertas:
                try:
                    frase = random.choice(frases)
                    legenda = (
                        f"{frase}\n\n"
                        f"<b>{oferta['titulo']}</b>\n"
                        f"<b>💰 {oferta['preco']}</b>\n\n"
                        f"👉 <a href='{oferta['link']}'>amazon.com.br</a>"
                    )
                    await bot.send_photo(chat_id=CHAT_ID, photo=oferta['imagem'], caption=legenda, parse_mode='HTML')
                    print(f"📤 Enviado: {oferta['titulo'][:50]}... | {oferta['preco']}")
                    await asyncio.sleep(30)  # espera 30 segundos entre ofertas
                except Exception as e:
                    print(f"⚠️ Erro ao enviar: {e}")
                    await asyncio.sleep(5)
        else:
            print("⚠️ Nenhuma oferta válida nesta rodada.")

        print("⏱️ Próxima rodada em 30 minutos.")
        rodada += 1
        await asyncio.sleep(1800)  # espera 30 minutos até a próxima rodada

if __name__ == '__main__':
    asyncio.run(enviar_ofertas())
