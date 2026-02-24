import json
data = {
    'sent': [
        'marivone.silva@hotmail.com',
        'caianahiago02@gmail.com',
        'espacolinikher@gmail.com',
        'medeirosoverral@gmail.com',
        'kaduriber15@gmail.com',
        'eloiza.lima0518@gmail.com',
        'nicolassiqueira51@gmail.com',
        'amarolaylson@gmail.com',
        'santosjardel179@gmail.com',
    ],
    'done': False
}
with open('/var/www/TREINACNH/email_progress.json', 'w') as f:
    json.dump(data, f)
print('Progresso inicializado com 9 emails ja enviados.')
