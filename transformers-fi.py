from transformers import pipeline

input = 'Mikäli yhteys veritulppiin voidaan vahvistaa, kyseessä olisi silti äärimmäisen harvinainen haittavaikutus. Esimerkiksi Britanniassa 18 miljoonasta Astra Zenecalla rokotetusta ihmisestä 30:n tiedettiin saaneen veritulppaoireita maaliskuun lopulle mentäessä, ja heistä seitsemän kuoli, kertoo BBC.'

translator = pipeline('translation_xx_to_yy', model='Helsinki-NLP/opus-mt-fi-en', tokenizer='Helsinki-NLP/opus-mt-fi-en')

output = translator(input)

print('Input:', input)
print('Output:', output[0]['translation_text'])