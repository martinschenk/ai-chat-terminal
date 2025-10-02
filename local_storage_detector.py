#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Local Storage Detector - Multilingual Keyword System
Detects user intent to save data locally or retrieve from local DB
Simple keyword matching without hardcoded PII types
"""

from typing import Tuple, Optional
import re

# Multilingual keywords for "save locally" intent
SAVE_KEYWORDS = {
    'de': [
        # Direct save commands
        'speichere lokal', 'speicher lokal', 'lokal speichern', 'speichere das lokal',
        'speicher das lokal', 'speichere dies lokal', 'speicher dies lokal',
        # Storage locations
        'auf meinem computer', 'auf meinem rechner', 'auf meiner festplatte',
        'in meiner datenbank', 'in meine datenbank', 'in meiner db', 'in meine db',
        'in meinem speicher', 'lokal ablegen', 'lokal sichern',
        # Memory/Remember commands
        'merke dir', 'merke dir das', 'merke dir dies', 'merk dir', 'merk dir das',
        'behalte das', 'behalte dies', 'behalte', 'erinnere dich daran',
        'vergiss das nicht', 'vergiss nicht', 'notiere das', 'notiere dir das',
        'schreib dir das auf', 'schreibe das auf', 'mach eine notiz',
        # Save variations
        'speichere', 'speicher', 'sichere', 'sichere das', 'sichere dies',
        'bewahre das auf', 'lege das ab', 'archiviere das',
        # Privacy-focused
        'privat speichern', 'vertraulich speichern', 'geheim speichern',
        'nicht online', 'offline speichern', 'nur lokal', 'bei mir speichern'
    ],
    'en': [
        # Direct save commands
        'save locally', 'save local', 'store locally', 'store local',
        'save this locally', 'store this locally', 'save it locally',
        # Storage locations
        'on my computer', 'on my machine', 'on my hard drive',
        'in my database', 'in my db', 'in my storage', 'locally',
        'save offline', 'store offline', 'keep offline',
        # Memory/Remember commands
        'remember this', 'remember that', 'remember it', 'remember',
        'keep this', 'keep that', 'keep it', 'don\'t forget this',
        'don\'t forget that', 'note this', 'note that', 'take a note',
        'write this down', 'write that down', 'make a note',
        # Save variations
        'save', 'store', 'save this', 'store this', 'save that', 'store that',
        'archive this', 'archive that', 'keep safe', 'save it',
        # Privacy-focused
        'save privately', 'store privately', 'save confidentially',
        'keep private', 'not online', 'offline only', 'local only'
    ],
    'es': [
        # Direct save commands
        'guarda localmente', 'guardar localmente', 'guarda local', 'guardar local',
        'guarda esto localmente', 'almacena localmente', 'almacenar localmente',
        # Storage locations
        'en mi ordenador', 'en mi computadora', 'en mi disco duro',
        'en mi base de datos', 'en mi db', 'en mi almacenamiento',
        'guardar offline', 'almacenar offline', 'sin conexión',
        # Memory/Remember commands
        'recuerda esto', 'recuerda eso', 'recuérdalo', 'acuérdate',
        'guarda esto', 'guarda eso', 'no olvides esto', 'no olvides',
        'anota esto', 'anota eso', 'toma nota', 'apunta esto',
        'escribe esto', 'haz una nota',
        # Save variations
        'guarda', 'guardar', 'almacena', 'almacenar', 'archiva',
        'conserva esto', 'guárdalo', 'almacénalo',
        # Privacy-focused
        'guardar privado', 'almacenar privado', 'guardar confidencial',
        'no online', 'solo local', 'privadamente'
    ],
    'fr': [
        # Direct save commands
        'sauvegarde localement', 'sauvegarde local', 'enregistre localement',
        'enregistre local', 'enregistrer localement', 'sauvegarde ça localement',
        'stocke localement', 'stocke local', 'garde localement',
        # Storage locations
        'sur mon ordinateur', 'sur ma machine', 'sur mon disque dur',
        'dans ma base de données', 'dans mon db', 'dans ma db',
        'en local', 'dans mon stockage', 'localement', 'chez moi',
        # Memory/Remember commands
        'souviens-toi', 'souviens-toi de ça', 'souviens-toi de cela',
        'retiens ça', 'retiens cela', 'mémorise ça', 'mémorise cela',
        'garde ça en mémoire', 'note ça', 'note cela', 'prends note',
        'écris ça', 'écris cela', 'fais une note', 'garde ça',
        # Save variations
        'sauvegarde', 'enregistre', 'stocke', 'conserve ça',
        'archive ça', 'mets ça de côté', 'préserve ça',
        # Privacy-focused
        'sauvegarde privé', 'enregistre privé', 'confidentiel',
        'pas en ligne', 'hors ligne', 'seulement local', 'uniquement local'
    ],
    'it': [
        # Direct save commands
        'salva localmente', 'salvare localmente', 'salva locale', 'salvare locale',
        'salva questo localmente', 'memorizza localmente', 'memorizzare localmente',
        # Storage locations
        'sul mio computer', 'sulla mia macchina', 'sul mio disco rigido',
        'nel mio database', 'nel mio db', 'nel mio archivio',
        'in locale', 'sul mio storage', 'localmente', 'da me',
        # Memory/Remember commands
        'ricorda questo', 'ricorda ciò', 'ricordalo', 'ricordati',
        'tieni questo', 'tieni ciò', 'memorizza questo', 'memorizza ciò',
        'non dimenticare', 'annota questo', 'annota ciò', 'prendi nota',
        'scrivi questo', 'scrivi ciò', 'fai una nota', 'conserva questo',
        # Save variations
        'salva', 'salvare', 'memorizza', 'memorizzare', 'archivia',
        'conserva', 'custodisci questo', 'mantieni questo',
        # Privacy-focused
        'salva privatamente', 'memorizza privatamente', 'salva confidenziale',
        'non online', 'offline', 'solo locale', 'unicamente locale'
    ],
    'pt': [
        # Direct save commands
        'salvar localmente', 'salve localmente', 'guardar localmente', 'guarde localmente',
        'salvar local', 'guardar local', 'armazenar localmente', 'armazene localmente',
        # Storage locations
        'no meu computador', 'na minha máquina', 'no meu disco rígido',
        'na minha base de dados', 'no meu db', 'no meu banco de dados',
        'em local', 'no meu armazenamento', 'localmente', 'comigo',
        # Memory/Remember commands
        'lembre-se disso', 'lembre disso', 'lembre-se', 'memorize isso',
        'memorize', 'guarde isso', 'guarde', 'não esqueça isso',
        'não esqueça', 'anote isso', 'anote', 'tome nota',
        'escreva isso', 'faça uma nota',
        # Save variations
        'salvar', 'salve', 'guardar', 'guarde', 'armazenar', 'armazene',
        'conservar', 'preservar', 'arquivar isso',
        # Privacy-focused
        'salvar privado', 'guardar privado', 'armazenar privado',
        'não online', 'offline', 'somente local', 'apenas local'
    ],
    'nl': [
        # Direct save commands
        'lokaal opslaan', 'sla lokaal op', 'bewaar lokaal', 'lokaal bewaren',
        'sla dit lokaal op', 'opslaan lokaal', 'bewaren lokaal',
        # Storage locations
        'op mijn computer', 'op mijn machine', 'op mijn harde schijf',
        'in mijn database', 'in mijn db', 'in mijn opslag',
        'lokaal', 'op mijn systeem', 'bij mij',
        # Memory/Remember commands
        'onthoud dit', 'onthoud dat', 'onthou', 'bewaar dit',
        'bewaar dat', 'houd dit', 'vergeet dit niet',
        'noteer dit', 'noteer dat', 'maak een notitie',
        'schrijf dit op', 'schrijf dat op',
        # Save variations
        'opslaan', 'sla op', 'bewaar', 'bewaren', 'archiveer',
        'sla dit op', 'bewaar dit veilig',
        # Privacy-focused
        'opslaan privé', 'bewaar privé', 'vertrouwelijk',
        'niet online', 'offline', 'alleen lokaal', 'uitsluitend lokaal'
    ],
    'pl': [
        # Direct save commands
        'zapisz lokalnie', 'zapisać lokalnie', 'przechowuj lokalnie', 'przechowywać lokalnie',
        'zapisz to lokalnie', 'zapisz lokalny', 'zapisywać lokalnie',
        # Storage locations
        'na moim komputerze', 'na mojej maszynie', 'na moim dysku',
        'w mojej bazie danych', 'w moim db', 'w mojej bazie',
        'lokalnie', 'w moim magazynie', 'u mnie',
        # Memory/Remember commands
        'zapamiętaj to', 'zapamiętaj', 'zapamiętać', 'zachowaj to',
        'zachowaj', 'zatrzymaj to', 'nie zapomnij tego',
        'nie zapomnij', 'zanotuj to', 'zanotuj', 'zrób notatkę',
        'zapisz to', 'zapisz sobie',
        # Save variations
        'zapisz', 'zapisać', 'przechowuj', 'przechowywać', 'zarchiwizuj',
        'zachowaj bezpiecznie', 'schowaj to',
        # Privacy-focused
        'zapisz prywatnie', 'przechowuj prywatnie', 'poufnie',
        'nie online', 'offline', 'tylko lokalnie', 'wyłącznie lokalnie'
    ],
    'ru': [
        # Direct save commands
        'сохрани локально', 'сохранить локально', 'сохрани локальный', 'храни локально',
        'сохрани это локально', 'сохранять локально', 'хранить локально',
        # Storage locations
        'на моём компьютере', 'на моей машине', 'на моём жёстком диске',
        'в моей базе данных', 'в моей бд', 'в моём db',
        'локально', 'в моём хранилище', 'у меня',
        # Memory/Remember commands
        'запомни это', 'запомни', 'запоминай', 'сохрани это',
        'сохрани', 'держи это', 'не забудь это',
        'не забудь', 'запиши это', 'запиши', 'сделай заметку',
        'записывай это', 'зафиксируй это',
        # Save variations
        'сохрани', 'сохранить', 'храни', 'хранить', 'архивируй',
        'сохрани надёжно', 'убери это',
        # Privacy-focused
        'сохрани приватно', 'храни приватно', 'конфиденциально',
        'не онлайн', 'офлайн', 'только локально', 'исключительно локально'
    ],
    'ja': [
        # Direct save commands
        'ローカルに保存', 'ローカル保存', 'ローカルで保存',
        'ローカルに保管', 'これをローカルに保存', 'ローカルに記録',
        # Storage locations
        '私のコンピューター', '私のマシン', '私のハードディスク',
        'データベースに保存', 'dbに保存', '私のデータベース',
        'ローカルストレージ', '私のストレージ', 'ローカルで',
        # Memory/Remember commands
        'これを覚えて', 'これを記憶', '覚えておいて', '記憶して',
        'これを保持', '保持して', '忘れないで', 'メモして',
        'これを記録', '記録して', 'ノートを取って', 'これを保存',
        # Save variations
        '保存', '保管', '記録', '保持', 'アーカイブ',
        '安全に保存', 'これを保管',
        # Privacy-focused
        'プライベートに保存', '機密保存', 'オフライン',
        'ローカルのみ', 'オンラインではない'
    ],
    'zh': [
        # Direct save commands
        '本地保存', '保存到本地', '本地存储', '在本地保存',
        '保存在本地', '本地储存', '本地记录',
        # Storage locations
        '在我的电脑', '在我的机器', '在我的硬盘',
        '在我的数据库', '在我的db', '在数据库中',
        '本地', '在我的存储', '在本地',
        # Memory/Remember commands
        '记住这个', '记住', '记下', '保存这个',
        '保存', '保留这个', '别忘了', '别忘记',
        '记录这个', '记录', '做笔记', '写下来',
        # Save variations
        '保存', '存储', '储存', '记录', '归档',
        '安全保存', '保管这个',
        # Privacy-focused
        '私密保存', '保密存储', '机密保存',
        '不在线', '离线', '仅本地', '只在本地'
    ],
    'ko': [
        # Direct save commands
        '로컬에 저장', '로컬 저장', '로컬로 저장', '로컬에 보관',
        '이것을 로컬에 저장', '로컬에 기록', '로컬로 보관',
        # Storage locations
        '내 컴퓨터에', '내 기기에', '내 하드드라이브에',
        '내 데이터베이스에', '내 db에', '데이터베이스에',
        '로컬', '내 저장소에', '로컬로',
        # Memory/Remember commands
        '이것을 기억해', '기억해', '기억해줘', '이것을 저장해',
        '저장해', '이것을 보관해', '잊지 마', '잊지 말아줘',
        '이것을 기록해', '기록해', '메모해', '적어줘',
        # Save variations
        '저장', '보관', '기록', '보존', '아카이브',
        '안전하게 저장', '이것을 보관',
        # Privacy-focused
        '비공개로 저장', '기밀로 저장', '프라이빗 저장',
        '온라인 아님', '오프라인', '로컬만', '로컬에만'
    ],
    'ar': [
        # Direct save commands
        'احفظ محليا', 'احفظ محلي', 'تخزين محلي', 'خزن محليا',
        'احفظ هذا محليا', 'احفظ محليًا', 'تخزين محليًا',
        # Storage locations
        'على جهازي', 'على جهاز الكمبيوتر', 'على القرص الصلب',
        'في قاعدة بياناتي', 'في db الخاص بي', 'في قاعدة البيانات',
        'محليا', 'في التخزين الخاص بي', 'عندي',
        # Memory/Remember commands
        'تذكر هذا', 'تذكر', 'احفظ في الذاكرة', 'احتفظ بهذا',
        'احتفظ', 'لا تنسى هذا', 'لا تنسى', 'سجل هذا',
        'سجل', 'اكتب هذا', 'دون هذا', 'خذ ملاحظة',
        # Save variations
        'احفظ', 'خزن', 'سجل', 'احتفظ', 'أرشف',
        'احفظ بأمان', 'احفظ هذا',
        # Privacy-focused
        'احفظ خاص', 'تخزين خاص', 'احفظ سري',
        'غير متصل', 'محلي فقط', 'محلي حصريا'
    ],
    'hi': [
        # Direct save commands
        'स्थानीय रूप से सहेजें', 'स्थानीय सहेजें', 'लोकल में सहेजें',
        'यह स्थानीय रूप से सहेजें', 'स्थानीय रूप से स्टोर करें',
        # Storage locations
        'मेरे कंप्यूटर पर', 'मेरी मशीन पर', 'मेरी हार्ड डिस्क पर',
        'मेरे डेटाबेस में', 'मेरे db में', 'डेटाबेस में',
        'स्थानीय', 'मेरे स्टोरेज में', 'लोकल में',
        # Memory/Remember commands
        'इसे याद रखें', 'याद रखें', 'याद रखो', 'इसे सहेजें',
        'सहेजें', 'इसे रखें', 'मत भूलना', 'इसे नोट करें',
        'नोट करें', 'लिख लें', 'नोट बनाएं',
        # Save variations
        'सहेजें', 'स्टोर करें', 'रिकॉर्ड करें', 'संग्रहित करें',
        'सुरक्षित रखें', 'इसे बचाएं',
        # Privacy-focused
        'निजी रूप से सहेजें', 'गोपनीय सहेजें', 'प्राइवेट सहेजें',
        'ऑफ़लाइन', 'केवल स्थानीय', 'सिर्फ लोकल'
    ],
    'tr': [
        # Direct save commands
        'yerel olarak kaydet', 'yerel kaydet', 'yerele kaydet',
        'bunu yerel olarak kaydet', 'yerel olarak sakla', 'lokal kaydet',
        # Storage locations
        'bilgisayarımda', 'makinemde', 'sabit diskimde',
        'veri tabanımda', 'db\'mde', 'veritabanımda',
        'yerel', 'depolama alanımda', 'lokal olarak',
        # Memory/Remember commands
        'bunu hatırla', 'hatırla', 'aklında tut', 'bunu kaydet',
        'kaydet', 'sakla', 'unutma', 'bunu not et',
        'not et', 'yaz', 'not al', 'kayıt et',
        # Save variations
        'kaydet', 'sakla', 'depolama', 'arşivle', 'muhafaza et',
        'güvenli kaydet', 'bunu sakla',
        # Privacy-focused
        'özel olarak kaydet', 'gizli kaydet', 'mahrem kaydet',
        'çevrimdışı', 'sadece yerel', 'yalnızca lokal'
    ],
    'sv': [
        # Direct save commands
        'spara lokalt', 'spara lokal', 'lagra lokalt', 'lagra lokal',
        'spara detta lokalt', 'förvara lokalt', 'spara på datorn',
        # Storage locations
        'på min dator', 'på min maskin', 'på min hårddisk',
        'i min databas', 'i min db', 'i mitt databasystem',
        'lokalt', 'i min lagring', 'hos mig',
        # Memory/Remember commands
        'kom ihåg detta', 'kom ihåg', 'minns detta', 'spara detta',
        'spara', 'behåll detta', 'glöm inte', 'anteckna detta',
        'anteckna', 'skriv ner', 'gör en anteckning',
        # Save variations
        'spara', 'lagra', 'arkivera', 'bevara', 'förvara',
        'spara säkert', 'behåll detta',
        # Privacy-focused
        'spara privat', 'lagra privat', 'spara konfidentiellt',
        'inte online', 'offline', 'endast lokalt', 'bara lokalt'
    ],
    'da': [
        # Direct save commands
        'gem lokalt', 'gem lokal', 'lagre lokalt', 'lagre lokal',
        'gem dette lokalt', 'opbevar lokalt', 'gem på computeren',
        # Storage locations
        'på min computer', 'på min maskine', 'på min harddisk',
        'i min database', 'i min db', 'i mit databasesystem',
        'lokalt', 'i min lagring', 'hos mig',
        # Memory/Remember commands
        'husk dette', 'husk', 'kom i hu', 'gem dette',
        'gem', 'behold dette', 'glem ikke', 'noter dette',
        'noter', 'skriv ned', 'lav en note',
        # Save variations
        'gem', 'lagre', 'arkiver', 'bevar', 'opbevar',
        'gem sikkert', 'behold dette',
        # Privacy-focused
        'gem privat', 'lagre privat', 'gem fortroligt',
        'ikke online', 'offline', 'kun lokalt', 'bare lokalt'
    ],
    'fi': [
        # Direct save commands
        'tallenna paikallisesti', 'tallenna paikallinen', 'säilytä paikallisesti',
        'tallenna tämä paikallisesti', 'tallenna koneelle', 'tallenna lokaalisti',
        # Storage locations
        'tietokoneellani', 'koneellani', 'kiintolevylleni',
        'tietokannassani', 'db:ssäni', 'tietokantajärjestelmässäni',
        'paikallisesti', 'tallennustilassani', 'minulla',
        # Memory/Remember commands
        'muista tämä', 'muista', 'pidä mielessä', 'tallenna tämä',
        'tallenna', 'säilytä tämä', 'älä unohda', 'merkitse tämä',
        'merkitse', 'kirjoita ylös', 'tee muistiinpano',
        # Save variations
        'tallenna', 'säilytä', 'arkistoi', 'säilö', 'pidä tallessa',
        'tallenna turvallisesti', 'säilytä tämä',
        # Privacy-focused
        'tallenna yksityisesti', 'säilytä yksityisesti', 'tallenna luottamuksellisesti',
        'ei verkossa', 'offline', 'vain paikallisesti', 'ainoastaan paikallisesti'
    ],
    'no': [
        # Direct save commands
        'lagre lokalt', 'lagre lokal', 'oppbevar lokalt', 'oppbevar lokal',
        'lagre dette lokalt', 'lagre på datamaskinen', 'lagre på maskinen',
        # Storage locations
        'på min datamaskin', 'på min maskin', 'på min harddisk',
        'i min database', 'i min db', 'i mitt databasesystem',
        'lokalt', 'i min lagring', 'hos meg',
        # Memory/Remember commands
        'husk dette', 'husk', 'kom ihåg', 'lagre dette',
        'lagre', 'behold dette', 'ikke glem', 'noter dette',
        'noter', 'skriv ned', 'lag en notis',
        # Save variations
        'lagre', 'oppbevar', 'arkiver', 'bevar', 'ta vare på',
        'lagre trygt', 'behold dette',
        # Privacy-focused
        'lagre privat', 'oppbevar privat', 'lagre konfidensielt',
        'ikke online', 'offline', 'kun lokalt', 'bare lokalt'
    ]
}

# Multilingual keywords for "retrieve from DB" intent
RETRIEVE_KEYWORDS = {
    'de': [
        # From database
        'aus meiner db', 'aus der db', 'aus meiner datenbank', 'aus der datenbank',
        'von meiner db', 'von meinem computer', 'von meinem rechner',
        'vom lokalen speicher', 'lokal gespeichert', 'lokal abgelegt',
        'in der db', 'in meiner db', 'in der datenbank', 'in meiner datenbank',
        # What did I save
        'was habe ich gespeichert', 'was hab ich gespeichert', 'was speicherte ich',
        'was habe ich notiert', 'was steht in meiner db', 'was ist gespeichert',
        # Show/Get data
        'zeige mir meine daten', 'zeig mir meine daten', 'hole meine daten',
        'gib mir meine daten', 'zeige gespeicherte', 'zeig gespeicherte',
        'zeige mir alles', 'zeig mir alles', 'zeige alles', 'alle daten',
        # Question variations
        'wie ist meine', 'wie lautet meine', 'welche ist meine', 'was ist meine',
        'wie war meine', 'wie heißt meine', 'welches ist mein',
        # Recall/Remember
        'erinnerst du dich', 'erinnerst du dich an', 'was weißt du über',
        'erinnere dich', 'was hast du über', 'hast du gespeichert',
        # Query local
        'meine lokalen daten', 'lokale daten', 'meine gespeicherten daten',
        'gespeicherte daten', 'was ist in der db', 'durchsuche meine db',
        # Memory questions
        'was weißt du', 'was kennst du', 'kennst du', 'weißt du'
    ],
    'en': [
        # From database
        'from my db', 'from the db', 'from my database', 'from the database',
        'from my computer', 'from my machine', 'from local storage',
        'locally stored', 'locally saved', 'saved locally',
        'in the db', 'in my db', 'in the database', 'in my database',
        # What did I save
        'what did i save', 'what did i store', 'what have i saved',
        'what did i note', 'what\'s in my db', 'what is stored',
        # Show/Get data
        'show my data', 'show me my data', 'get my data',
        'give me my data', 'show stored', 'retrieve my data',
        # Question variations
        'what is my', 'what\'s my', 'what was my', 'which is my',
        'how is my', 'tell me my',
        # Recall/Remember
        'do you remember', 'remember what', 'what do you know about',
        'recall', 'what do you have about', 'have you saved',
        # Query local
        'my local data', 'local data', 'my stored data', 'stored data',
        'what\'s in the db', 'search my db', 'query my db',
        # Memory questions
        'what do you know', 'do you know', 'you know'
    ],
    'es': [
        # From database
        'de mi db', 'de la db', 'de mi base de datos', 'de la base de datos',
        'de mi ordenador', 'de mi computadora', 'del almacenamiento local',
        'guardado localmente', 'almacenado localmente',
        'en la db', 'en mi db', 'en la base de datos', 'en mi base de datos',
        # What did I save
        'qué guardé', 'qué almacené', 'qué he guardado', 'qué anoté',
        'qué hay en mi db', 'qué está guardado',
        # Show/Get data
        'muestra mis datos', 'muéstrame mis datos', 'dame mis datos',
        'obtén mis datos', 'muestra guardados', 'recupera mis datos',
        # Question variations
        'cuál es mi', 'cómo es mi', 'qué es mi', 'cuál era mi',
        'dime mi', 'cual es mi',
        # Recall/Remember
        'te acuerdas', 'recuerdas', 'qué sabes sobre', 'qué tienes sobre',
        'has guardado', 'recuerda',
        # Query local
        'mis datos locales', 'datos locales', 'mis datos guardados',
        'datos guardados', 'qué hay en la db', 'busca en mi db',
        # Memory questions
        'qué sabes', 'sabes', 'conoces'
    ],
    'fr': [
        # From database
        'de ma db', 'de la db', 'de ma base de données', 'de la base de données',
        'de mon ordinateur', 'de ma machine', 'du stockage local',
        'sauvegardé localement', 'enregistré localement', 'stocké localement',
        # What did I save
        'qu\'ai-je sauvegardé', 'qu\'ai-je enregistré', 'qu\'ai-je stocké',
        'qu\'ai-je noté', 'qu\'y a-t-il dans ma db', 'qu\'est-ce qui est sauvegardé',
        # Show/Get data
        'montre mes données', 'montre-moi mes données', 'donne mes données',
        'donne-moi mes données', 'affiche mes données', 'récupère mes données',
        # Recall/Remember
        'te souviens-tu', 'tu te souviens', 'que sais-tu sur', 'qu\'as-tu sur',
        'as-tu sauvegardé', 'rappelle-toi', 'souviens-toi',
        # Query local
        'mes données locales', 'données locales', 'mes données sauvegardées',
        'données sauvegardées', 'qu\'y a-t-il dans la db', 'cherche dans ma db',
        # Memory questions
        'que sais-tu', 'sais-tu', 'connais-tu', 'tu sais'
    ],
    'it': [
        # From database
        'dal mio db', 'dal db', 'dal mio database', 'dalla mia base di dati',
        'dal mio computer', 'dalla mia macchina', 'dallo storage locale',
        'salvato localmente', 'memorizzato localmente', 'archiviato localmente',
        # What did I save
        'cosa ho salvato', 'cosa ho memorizzato', 'cosa ho archiviato',
        'cosa ho annotato', 'cosa c\'è nel mio db', 'cosa è salvato',
        # Show/Get data
        'mostra i miei dati', 'mostrami i miei dati', 'dammi i miei dati',
        'fornisci i miei dati', 'visualizza i dati', 'recupera i miei dati',
        # Recall/Remember
        'ti ricordi', 'ricordi', 'cosa sai su', 'cosa hai su',
        'hai salvato', 'ricorda', 'ricordati',
        # Query local
        'i miei dati locali', 'dati locali', 'i miei dati salvati',
        'dati salvati', 'cosa c\'è nel db', 'cerca nel mio db',
        # Memory questions
        'cosa sai', 'sai', 'conosci', 'lo sai'
    ],
    'pt': [
        # From database
        'do meu db', 'do db', 'da minha base de dados', 'do banco de dados',
        'do meu computador', 'da minha máquina', 'do armazenamento local',
        'salvo localmente', 'guardado localmente', 'armazenado localmente',
        # What did I save
        'o que eu salvei', 'o que eu guardei', 'o que eu armazenei',
        'o que eu anotei', 'o que está no meu db', 'o que está salvo',
        # Show/Get data
        'mostre meus dados', 'mostre-me meus dados', 'me dê meus dados',
        'dê-me meus dados', 'exiba meus dados', 'recupere meus dados',
        # Recall/Remember
        'você se lembra', 'lembra', 'o que você sabe sobre', 'o que você tem sobre',
        'você salvou', 'lembre-se', 'recordar',
        # Query local
        'meus dados locais', 'dados locais', 'meus dados salvos',
        'dados salvos', 'o que está no db', 'busque no meu db',
        # Memory questions
        'o que você sabe', 'você sabe', 'conhece', 'sabe'
    ],
    'nl': [
        # From database
        'uit mijn db', 'uit de db', 'uit mijn database', 'uit de database',
        'van mijn computer', 'van mijn machine', 'uit lokale opslag',
        'lokaal opgeslagen', 'lokaal bewaard', 'lokaal geplaatst',
        # What did I save
        'wat heb ik opgeslagen', 'wat heb ik bewaard', 'wat sloeg ik op',
        'wat heb ik genoteerd', 'wat zit er in mijn db', 'wat is opgeslagen',
        # Show/Get data
        'toon mijn gegevens', 'laat mijn gegevens zien', 'geef mijn gegevens',
        'geef me mijn gegevens', 'haal mijn gegevens op', 'toon opgeslagen',
        # Recall/Remember
        'weet je nog', 'herinner je', 'wat weet je over', 'wat heb je over',
        'heb je opgeslagen', 'herinner', 'onthoud je',
        # Query local
        'mijn lokale gegevens', 'lokale gegevens', 'mijn opgeslagen gegevens',
        'opgeslagen gegevens', 'wat zit in de db', 'zoek in mijn db',
        # Memory questions
        'wat weet je', 'weet je', 'ken je', 'je weet'
    ],
    'pl': [
        # From database
        'z mojej db', 'z db', 'z mojej bazy danych', 'z bazy danych',
        'z mojego komputera', 'z mojej maszyny', 'z lokalnego magazynu',
        'zapisane lokalnie', 'przechowywane lokalnie', 'zachowane lokalnie',
        # What did I save
        'co zapisałem', 'co zachowałem', 'co przechowałem',
        'co zanotowałem', 'co jest w mojej db', 'co jest zapisane',
        # Show/Get data
        'pokaż moje dane', 'pokaż mi moje dane', 'daj moje dane',
        'daj mi moje dane', 'wyświetl moje dane', 'odzyskaj moje dane',
        # Recall/Remember
        'pamiętasz', 'czy pamiętasz', 'co wiesz o', 'co masz o',
        'zapisałeś', 'przypomnij sobie', 'zapamiętaj',
        # Query local
        'moje lokalne dane', 'dane lokalne', 'moje zapisane dane',
        'zapisane dane', 'co jest w db', 'przeszukaj moją db',
        # Memory questions
        'co wiesz', 'wiesz', 'znasz', 'czy wiesz'
    ],
    'ru': [
        # From database
        'из моей бд', 'из бд', 'из моей базы данных', 'из базы данных',
        'с моего компьютера', 'с моей машины', 'из локального хранилища',
        'сохранено локально', 'хранится локально', 'записано локально',
        # What did I save
        'что я сохранил', 'что я записал', 'что я сохранял',
        'что я запомнил', 'что в моей бд', 'что сохранено',
        # Show/Get data
        'покажи мои данные', 'покажи данные', 'дай мои данные',
        'дай мне данные', 'отобрази данные', 'извлеки мои данные',
        # Recall/Remember
        'помнишь', 'ты помнишь', 'что знаешь о', 'что у тебя о',
        'сохранял ли ты', 'вспомни', 'запомнил',
        # Query local
        'мои локальные данные', 'локальные данные', 'мои сохраненные данные',
        'сохраненные данные', 'что в бд', 'найди в моей бд',
        # Memory questions
        'что знаешь', 'знаешь', 'ты знаешь', 'известно ли'
    ],
    'ja': [
        # From database
        '私のdbから', 'dbから', '私のデータベースから', 'データベースから',
        '私のコンピューターから', '私のマシンから', 'ローカルストレージから',
        'ローカルに保存', 'ローカルに保管', 'ローカルに記録',
        # What did I save
        '何を保存したか', '何を保管したか', '何を記録したか',
        '何をメモしたか', '私のdbに何があるか', '何が保存されているか',
        # Show/Get data
        '私のデータを表示', 'データを表示', '私のデータを取得',
        'データをください', '保存データを表示', 'データを取り出して',
        # Recall/Remember
        '覚えていますか', '覚えている', '何を知っている', '何がある',
        '保存しましたか', '思い出して', '記憶している',
        # Query local
        '私のローカルデータ', 'ローカルデータ', '私の保存データ',
        '保存したデータ', 'dbに何がある', '私のdbを検索',
        # Memory questions
        '何を知っている', '知っている', 'わかる', 'ご存知'
    ],
    'zh': [
        # From database
        '从我的db', '从db', '从我的数据库', '从数据库',
        '从我的电脑', '从我的机器', '从本地存储',
        '本地保存的', '本地储存的', '本地记录的',
        # What did I save
        '我保存了什么', '我储存了什么', '我记录了什么',
        '我记下了什么', '我的db里有什么', '保存了什么',
        # Show/Get data
        '显示我的数据', '给我看数据', '给我数据',
        '取出数据', '显示保存的', '检索数据',
        # Recall/Remember
        '你记得吗', '记得', '你知道什么', '你有什么',
        '保存过吗', '回忆', '记住了',
        # Query local
        '我的本地数据', '本地数据', '我保存的数据',
        '保存的数据', 'db里有什么', '搜索我的db',
        # Memory questions
        '你知道什么', '知道', '了解', '你知道'
    ],
    'ko': [
        # From database
        '내 db에서', 'db에서', '내 데이터베이스에서', '데이터베이스에서',
        '내 컴퓨터에서', '내 기기에서', '로컬 저장소에서',
        '로컬에 저장된', '로컬에 보관된', '로컬에 기록된',
        # What did I save
        '내가 저장한 것', '내가 보관한 것', '내가 기록한 것',
        '내가 메모한 것', '내 db에 뭐가 있어', '저장된 것',
        # Show/Get data
        '내 데이터 표시', '데이터 보여줘', '내 데이터 줘',
        '데이터 가져와', '저장된 데이터 표시', '데이터 검색',
        # Recall/Remember
        '기억해', '기억하니', '뭘 알아', '뭐 있어',
        '저장했어', '기억해줘', '기억하고 있어',
        # Query local
        '내 로컬 데이터', '로컬 데이터', '내가 저장한 데이터',
        '저장한 데이터', 'db에 뭐가 있어', '내 db 검색',
        # Memory questions
        '뭘 알아', '알아', '아니', '알고 있어'
    ],
    'ar': [
        # From database
        'من db الخاص بي', 'من db', 'من قاعدة بياناتي', 'من قاعدة البيانات',
        'من جهازي', 'من جهاز الكمبيوتر', 'من التخزين المحلي',
        'محفوظ محليا', 'مخزن محليا', 'مسجل محليا',
        # What did I save
        'ماذا حفظت', 'ماذا خزنت', 'ماذا سجلت',
        'ماذا دونت', 'ماذا في db الخاص بي', 'ماذا محفوظ',
        # Show/Get data
        'أظهر بياناتي', 'أرني بياناتي', 'أعطني بياناتي',
        'أحضر بياناتي', 'اعرض البيانات', 'استرجع بياناتي',
        # Recall/Remember
        'هل تتذكر', 'تتذكر', 'ماذا تعرف عن', 'ماذا لديك عن',
        'هل حفظت', 'تذكر', 'تذكرت',
        # Query local
        'بياناتي المحلية', 'البيانات المحلية', 'بياناتي المحفوظة',
        'البيانات المحفوظة', 'ماذا في db', 'ابحث في db الخاص بي',
        # Memory questions
        'ماذا تعرف', 'تعرف', 'هل تعلم', 'أتعرف'
    ],
    'hi': [
        # From database
        'मेरे db से', 'db से', 'मेरे डेटाबेस से', 'डेटाबेस से',
        'मेरे कंप्यूटर से', 'मेरी मशीन से', 'स्थानीय स्टोरेज से',
        'स्थानीय रूप से सहेजा', 'स्थानीय रूप से स्टोर किया', 'लोकल में सहेजा',
        # What did I save
        'मैंने क्या सहेजा', 'मैंने क्या स्टोर किया', 'मैंने क्या रिकॉर्ड किया',
        'मैंने क्या नोट किया', 'मेरे db में क्या है', 'क्या सहेजा है',
        # Show/Get data
        'मेरा डेटा दिखाएं', 'मुझे मेरा डेटा दिखाएं', 'मेरा डेटा दें',
        'मुझे डेटा दें', 'सहेजा डेटा दिखाएं', 'मेरा डेटा लाएं',
        # Recall/Remember
        'क्या आपको याद है', 'याद है', 'आप क्या जानते हैं', 'आपके पास क्या है',
        'क्या आपने सहेजा', 'याद करें', 'याद रखा',
        # Query local
        'मेरा स्थानीय डेटा', 'स्थानीय डेटा', 'मेरा सहेजा डेटा',
        'सहेजा डेटा', 'db में क्या है', 'मेरे db में खोजें',
        # Memory questions
        'आप क्या जानते हैं', 'जानते हैं', 'पता है', 'आपको पता है'
    ],
    'tr': [
        # From database
        'db\'mden', 'db\'den', 'veri tabanımdan', 'veri tabanından',
        'bilgisayarımdan', 'makinemden', 'yerel depolamadan',
        'yerel olarak kaydedilmiş', 'yerel olarak saklanmış', 'lokalde kayıtlı',
        # What did I save
        'ne kaydettim', 'ne sakladım', 'ne arşivledim',
        'ne not ettim', 'db\'mde ne var', 'ne kayıtlı',
        # Show/Get data
        'verilerimi göster', 'bana verilerimi göster', 'verilerimi ver',
        'bana ver', 'kayıtlı verileri göster', 'verilerimi getir',
        # Recall/Remember
        'hatırlıyor musun', 'hatırlıyor', 'ne biliyorsun', 'neyln var',
        'kaydettim mi', 'hatırla', 'aklında mı',
        # Query local
        'yerel verilerim', 'yerel veriler', 'kaydettiğim veriler',
        'kayıtlı veriler', 'db\'de ne var', 'db\'mde ara',
        # Memory questions
        'ne biliyorsun', 'biliyor musun', 'bilir misin', 'biliyorsun'
    ],
    'sv': [
        # From database
        'från min db', 'från db', 'från min databas', 'från databasen',
        'från min dator', 'från min maskin', 'från lokal lagring',
        'lokalt sparad', 'lokalt lagrad', 'lokalt förvarat',
        # What did I save
        'vad har jag sparat', 'vad har jag lagrat', 'vad sparade jag',
        'vad antecknade jag', 'vad finns i min db', 'vad är sparat',
        # Show/Get data
        'visa min data', 'visa mig min data', 'ge mig min data',
        'hämta min data', 'visa sparad data', 'ta fram data',
        # Recall/Remember
        'kommer du ihåg', 'minns du', 'vad vet du om', 'vad har du om',
        'har du sparat', 'kom ihåg', 'minns',
        # Query local
        'min lokala data', 'lokal data', 'mina sparade data',
        'sparad data', 'vad finns i db', 'sök i min db',
        # Memory questions
        'vad vet du', 'vet du', 'känner du till', 'du vet'
    ],
    'da': [
        # From database
        'fra min db', 'fra db', 'fra min database', 'fra databasen',
        'fra min computer', 'fra min maskine', 'fra lokal lagring',
        'lokalt gemt', 'lokalt lagret', 'lokalt opbevaret',
        # What did I save
        'hvad har jeg gemt', 'hvad har jeg lagret', 'hvad gemte jeg',
        'hvad noterede jeg', 'hvad er i min db', 'hvad er gemt',
        # Show/Get data
        'vis mine data', 'vis mig mine data', 'giv mig mine data',
        'hent mine data', 'vis gemte data', 'hent data',
        # Recall/Remember
        'husker du', 'kan du huske', 'hvad ved du om', 'hvad har du om',
        'har du gemt', 'husk', 'kom i hu',
        # Query local
        'min lokale data', 'lokal data', 'mine gemte data',
        'gemte data', 'hvad er i db', 'søg i min db',
        # Memory questions
        'hvad ved du', 'ved du', 'kender du', 'du ved'
    ],
    'fi': [
        # From database
        'omasta db:stä', 'db:stä', 'omasta tietokannasta', 'tietokannasta',
        'tietokoneeltani', 'koneeltani', 'paikallisesta tallennustilasta',
        'paikallisesti tallennettu', 'paikallisesti säilytetty', 'lokaalisti tallennettu',
        # What did I save
        'mitä tallensin', 'mitä säilytin', 'mitä arkistoin',
        'mitä merkitsin', 'mitä on db:ssäni', 'mikä on tallennettu',
        # Show/Get data
        'näytä tietoni', 'näytä minulle tietoni', 'anna tietoni',
        'hae tietoni', 'näytä tallennetut', 'hae data',
        # Recall/Remember
        'muistatko', 'muistatko sinä', 'mitä tiedät', 'mitä sinulla on',
        'tallensitko', 'muista', 'pidä mielessä',
        # Query local
        'paikalliset tietoni', 'paikallinen data', 'tallennetut tiedot',
        'tallennettu data', 'mitä db:ssä on', 'etsi db:stäni',
        # Memory questions
        'mitä tiedät', 'tiedätkö', 'tiedätkö sinä', 'sinä tiedät'
    ],
    'no': [
        # From database
        'fra min db', 'fra db', 'fra min database', 'fra databasen',
        'fra min datamaskin', 'fra min maskin', 'fra lokal lagring',
        'lokalt lagret', 'lokalt oppbevart', 'lokalt arkivert',
        # What did I save
        'hva har jeg lagret', 'hva har jeg oppbevart', 'hva lagret jeg',
        'hva noterte jeg', 'hva er i min db', 'hva er lagret',
        # Show/Get data
        'vis mine data', 'vis meg mine data', 'gi meg mine data',
        'hent mine data', 'vis lagrede data', 'hent data',
        # Recall/Remember
        'husker du', 'kan du huske', 'hva vet du om', 'hva har du om',
        'har du lagret', 'husk', 'kom ihåg',
        # Query local
        'min lokale data', 'lokal data', 'mine lagrede data',
        'lagrede data', 'hva er i db', 'søk i min db',
        # Memory questions
        'hva vet du', 'vet du', 'kjenner du', 'du vet'
    ]
}


class LocalStorageDetector:
    """Detects user intent for local storage operations via keywords"""

    def __init__(self):
        """Initialize detector with all keyword dictionaries"""
        self.save_keywords = SAVE_KEYWORDS
        self.retrieve_keywords = RETRIEVE_KEYWORDS

    def detect_save_locally(self, text: str) -> bool:
        """
        Detect if user wants to save data locally

        Args:
            text: User input message

        Returns:
            True if save intent detected, False otherwise
        """
        text_lower = text.lower()

        # Check all languages
        for lang, keywords in self.save_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return True

        return False

    def detect_retrieve_from_db(self, text: str) -> bool:
        """
        Detect if user wants to retrieve data from local DB

        Args:
            text: User input message

        Returns:
            True if retrieve intent detected, False otherwise
        """
        text_lower = text.lower()

        # Check all languages
        for lang, keywords in self.retrieve_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return True

        return False

    def get_intent(self, text: str) -> Tuple[str, bool]:
        """
        Detect user intent from text

        Args:
            text: User input message

        Returns:
            Tuple of (intent_type, detected)
            intent_type: 'save_local', 'retrieve_local', or 'normal'
            detected: True if keyword detected, False otherwise
        """
        # Check RETRIEVE first - higher priority than SAVE
        # (e.g. "zeige mir was gespeichert ist" should be RETRIEVE, not SAVE)
        if self.detect_retrieve_from_db(text):
            return ('retrieve_local', True)
        elif self.detect_save_locally(text):
            return ('save_local', True)
        else:
            return ('normal', False)


# For testing
if __name__ == '__main__':
    detector = LocalStorageDetector()

    # Test cases
    test_cases = [
        # German
        ("speichere lokal: mein API Key ist abc123", True, 'save'),
        ("was ist aus meiner db über Python?", True, 'retrieve'),
        ("wie geht es dir?", False, None),

        # English
        ("save locally: my password is secret123", True, 'save'),
        ("what do I have from my database?", True, 'retrieve'),
        ("tell me a joke", False, None),

        # Spanish
        ("guarda localmente: mi correo es test@example.com", True, 'save'),
        ("qué guardé de mi db?", True, 'retrieve'),

        # Mixed
        ("Ich möchte das lokal speichern: wichtige Info", True, 'save'),
        ("Zeige mir meine lokalen daten über API", True, 'retrieve'),
    ]

    print("🧪 Testing Local Storage Detector\n")

    for text, should_detect, intent_type in test_cases:
        intent, detected = detector.get_intent(text)

        if intent_type == 'save':
            expected_intent = 'save_local'
        elif intent_type == 'retrieve':
            expected_intent = 'retrieve_local'
        else:
            expected_intent = 'normal'

        status = "✅" if (detected == should_detect and intent == expected_intent) else "❌"
        print(f"{status} '{text[:50]}...'")
        print(f"   Expected: {expected_intent}, Got: {intent}\n")
