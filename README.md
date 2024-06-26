# ErythroScope Project

## Pași pentru Clonare

Pentru a clona repository-ul, folosiți următoarea comandă:

```
git clone https://github.com/Raphael-Augustinov/ErythroScope
cd ErythroScope
```

## Instalarea Dependențelor

După ce ați clonat repository-ul, instalați toate dependențele necesare utilizând fișierul requirements.txt. Utilizați următoarea comandă:

```
pip install -r requirements.txt
```

## Descărcarea Modelului AI

Modelul AI antrenat este necesar pentru a rula aplicația. Puteți descărca modelul AI accesând link-ul de mai jos:

https://drive.google.com/file/d/1-TQeoMUcYv-JGlBwP0MAV215hPBHvAjq/view?usp=drive_link

După descărcare, plasați fișierul modelului în directorul ErythroScopeApp/model/ din repository.

## Lansarea Aplicației

După ce toate dependențele sunt instalate și modelul AI este plasat în directorul corect, lansați aplicația folosind următoarea comandă:

```
cd ErythroScopeApp
python app.py
```
## Testarea Modelului

Încărcați imaginile din directorul demo_images/ în aplicație și apăsați butonul Analyze images. Rezultatele analizei vor apărea în partea de jos a ecranului.

