# Ingestion incrémentale de logs JSONL — offsets, plafonds, idempotence

Mécanique à respecter pour tout ingesteur qui reprend un fichier de log là où il s'est arrêté
(Pipeline Inspector de Life_mean_realm et tout équivalent).

## 1. Les offsets renvoyés doivent être ABSOLUS

Piège classique :

```python
fh.seek(start_offset)
pos = 0                      # ← le bug
while (chunk := fh.readline()):
    pos += len(chunk)
    yield ev, pos            # offset relatif au point de reprise
```

L'appelant stocke `pos` comme position absolue. À la reprise suivante, l'offset a *rétréci* :
le lecteur repart au milieu d'une ligne, relit du contenu déjà consommé ou s'arrête au mauvais
endroit — sans lever d'exception.

Correctif : lire depuis le début, sauter les lignes entièrement consommées, renvoyer la position
réelle.

```python
pos = 0
line_no = 0
while (chunk := fh.readline()):
    pos += len(chunk)
    line_no += 1
    if pos <= start_offset:      # ligne déjà consommée
        continue
    if not chunk.endswith(b"\n"):  # ligne partielle : ne pas la consommer
        break
    yield line_no, chunk.decode("utf-8", errors="replace").strip(), pos
```

Coût linéaire assumé (≈1 s pour 85 Mo) ; la justesse des offsets et des numéros de ligne prime.
Enregistrer `line_no` réel rend aussi `source_line` exploitable pour remonter au journal d'origine.

## 2. Un plafond par fichier exige un drapeau, sinon le reste est perdu

Un `max_records_per_file` (ex. 200 000) coupe la lecture d'un gros fichier. Si l'état persiste
`size == st_size` sans autre marque, la passe suivante considère le fichier comme entièrement
consommé et **ne relit jamais la suite**. Aucune erreur n'est signalée.

- Ajouter une colonne `truncated` (migration `ALTER TABLE ingest_state ADD COLUMN truncated INTEGER NOT NULL DEFAULT 0`).
- La condition « fichier déjà ingéré » doit inclure `and not state['truncated']`.
- Enregistrer l'`offset` du dernier enregistrement émis, pas la taille du fichier.
- Message d'erreur explicite : `plafond N atteint (reprise à l'offset X)`.

Réparer un état hérité : `UPDATE ingest_state SET truncated=1 WHERE events >= <plafond>`.
Vérifier ensuite que `offset == size` et `truncated == 0` : c'est la preuve que le fichier est
réellement consommé en entier. Un fichier plus gros que le plafond demande **deux passes** —
le documenter au lieu de laisser croire à une ingestion complète en une exécution.

## 3. Idempotence et déduplication

- `event_id` stable (hash de type + fichier + ligne + horodatage) et `INSERT OR IGNORE`.
- Contrôle : `SELECT count(*) - count(distinct event_id) FROM events` doit valoir 0.
- Contrôle de reprise : deux passes consécutives sans modification → `events_added == 0`.
- Un compteur `bytes_read` déclaré mais jamais incrémenté se lit comme un bug de lecture :
  l'alimenter avec la taille réellement examinée rend les passes comparables.

## 4. Ce que l'ingesteur ne doit pas faire

- Ne pas réécrire ni tronquer le journal d'origine : l'état d'ingestion est une *cache dérivée*,
  reconstructible ; supprimer et reconstruire cette cache est acceptable, toucher aux logs non.
- Ne pas déduire une corrélation causale d'un simple identifiant de regroupement. `run_id`,
  `session_id`, `generation_id` prouvent l'appartenance à un même run → corrélation **probable**.
  Seuls un `model_call_id` ou un `correlation_id` d'audit autorisent « explicite ».

## 5. Vérification rapide

```python
c.execute("select correlation,count(*) from events group by correlation")
c.execute("select path,offset,size,truncated from ingest_state where truncated=1")
c.execute("select count(*) - count(distinct event_id) from events")
```
