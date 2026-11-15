from __future__ import annotations
# D-020: dictionary hook for common product terms; real MT via TRANSLATE_API_URL env when configured.
TERMS={"headphones":{"de":"Kopfhörer","fr":"casque","es":"auriculares","ar":"سماعات","ur":"ہیڈ فون","hi":"हेडफोन","zh":"耳机","ja":"ヘッドホン","ko":"헤드폰","pl":"słuchawki","tr":"kulaklık"},
"phone":{"de":"Handy","fr":"téléphone","es":"teléfono","ar":"هاتف","ur":"فون","hi":"फोन","zh":"手机","ja":"スマートフォン","ko":"휴대폰","pl":"telefon","tr":"telefon"},
"laptop":{"de":"Laptop","fr":"ordinateur portable","es":"portátil","ar":"لابتوب","ur":"لیپ ٹاپ","hi":"लैपटॉप","zh":"笔记本电脑","ja":"ノートパソコン","ko":"노트북","pl":"laptop","tr":"dizüstü"}}
LOCALE_LANG={"amazon.de":"de","amazon.fr":"fr","amazon.es":"es","amazon.co.jp":"ja","allegro":"pl","trendyol":"tr"}
def translate_query(query: str, lang: str) -> str:
    out=query.lower()
    for en, mp in TERMS.items():
        if en in out and lang in mp: out=out.replace(en, mp[lang])
    return out
