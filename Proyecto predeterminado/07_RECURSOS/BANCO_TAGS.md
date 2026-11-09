# Banco de tags

Los tags son el 50% de la distribución en KLIPY. Un buen clip con tags malos no aparece; un clip normal con tags exactos sí.

---

## La fórmula

```text
3 amplios + 5 específicos + 3 emoción + 2 contexto + 2 en inglés = 15
```

No es una regla matemática, es una forma de no olvidar nada.

### Ejemplo

Clip: gato que salta asustado cuando suena el timbre.

```text
gato, gato asustado, mascota, animal, reaccion, sorpresa, shock,
miedo, gracioso, divertido, timbre, casa,
scared cat, surprised cat, funny cat
```

- Amplios: gato, mascota, animal.
- Específicos: gato asustado, reaccion, timbre, casa.
- Emoción: sorpresa, shock, miedo.
- Contexto: timbre, casa.
- Inglés: scared cat, surprised cat, funny cat.

---

## Tags por nicho

### Fútbol

**Español**

```text
futbol, soccer, gol, golazo, celebracion, jugador, partido, estadio,
aficion, hincha, penal, atajada, regate, fallo, victoria, derrota,
epico, frustracion, ultimo minuto, liga
```

**Inglés**

```text
football, soccer, goal, celebration, player, match, stadium, fans,
penalty, save, skill, fail, victory, defeat, epic, last minute, league
```

### Gaming

**Español**

```text
gaming, videojuego, gameplay, gamer, partida, clutch, fail, victoria,
derrota, reaccion, rage, glitch, speedrun, npc, jefe final, risa,
frustracion, jugada epica, multijugador, stream
```

**Inglés**

```text
gaming, videogame, gameplay, gamer, match, clutch, fail, victory,
defeat, reaction, rage, glitch, speedrun, npc, boss, funny,
frustration, epic play, multiplayer, stream
```

### Memes y reacciones

**Español**

```text
memes, reaccion, humor, risa, gracioso, divertido, cuando, pov, yo,
esperando, sorpresa, confusion, cringe, lunes, viernes, chat, situacion,
no puede ser, cara de, meme
```

**Inglés**

```text
memes, reaction, humor, laugh, funny, when, pov, me, waiting,
surprised, confused, cringe, monday, friday, relatable, situation,
no way, face, meme, reaction image
```

### Animales

**Español**

```text
animales, gato, perro, mascota, cachorro, gatito, gracioso, tierno,
reaccion, miedo, sorpresa, jugando, durmiendo, comiendo, rescate,
felino, canino, divertido, adorable, animal gracioso
```

**Inglés**

```text
animals, cat, dog, pet, puppy, kitten, funny, cute, reaction, scared,
surprised, playing, sleeping, eating, rescue, feline, canine, adorable,
funny animal, pet reaction
```

---

## Tags de emoción

| Emoción | Español | Inglés |
|---|---|---|
| Risa | risa, gracioso, divertido, muerto de risa | laugh, funny, hilarious, dying of laughter |
| Sorpresa | sorpresa, shock, no puede ser, increible | surprised, shock, no way, unexpected |
| Frustración | frustrado, enojado, rabia, harto | frustrated, angry, rage, fed up |
| Tristeza | triste, llorando, decepcionado | sad, crying, disappointed |
| Amor | amor, corazon, enamorado, cariño | love, heart, crush, romantic |
| Orgullo | orgullo, victoria, lo logre, epico | proud, victory, win, epic |
| Confusión | confusion, no entiendo, qué | confused, huh, what |
| Aburrimiento | aburrido, esperando, lunes | bored, waiting, monday |
| Vergüenza | vergüenza, cringe, ay no | embarrassed, cringe, oh no |
| Miedo | miedo, asustado, terror | scared, fear, terrified |

---

## Tags de situación

Úsalos solo si el clip realmente muestra la situación:

```text
lunes, viernes, reunion, examen, trabajo, jefe, escuela, chat,
notificacion, esperando, tarde, dormir, comida, cafe, trafico,
videojuego, partido, cumpleaños, fila, wifi
```

En inglés:

```text
monday, friday, meeting, exam, work, boss, school, chat,
notification, waiting, late, sleep, food, coffee, traffic,
gaming, match, birthday, line, wifi
```

---

## Cómo elegir los 15

1. Escribe qué se ve en 3 palabras.
2. Añade el sujeto (gato, jugador, gamer).
3. Añade la acción (salta, celebra, falla).
4. Añade la emoción (sorpresa, risa, furia).
5. Añade el contexto (timbre, estadio, partida).
6. Añade sinónimos en inglés.
7. Elimina cualquier tag que no puedas defender mirando el clip.

Si dudas, quita el tag. **Un tag irrelevante puede hacer que rechacen todo el clip.**

---

## Tags que no debes usar

- Tendencias que no aparecen en el clip.
- Nombres de personas famosas que no salen.
- "Free", "follow", "subscribe", "like".
- Palabras de otras plataformas: "tiktok", "reels", "shorts".
- Insultos, slurs o contenido sexual.
- Errores de ortografía obvios.
- Letras sueltas o números sin sentido.
- Repeticiones: "gato, gato, gato, gatos, gatito, gatitos".
- Tags en 5 idiomas que no entiendes.

---

## Bilingüe sin exagerar

Si tu audiencia es global:

- 8-10 tags en español.
- 5-7 tags en inglés.
- No dupliques la misma palabra en ambos idiomas si no aporta.
- El título puede ir en el idioma principal; los tags cubren las búsquedas.

Si tu audiencia es solo local, prioriza ese idioma y añade 3-4 en inglés.

---

## Generador rápido

```powershell
python 08_AUTOMATIZACION\klipy.py ficha "gato asustado por el timbre" --nicho animales --emocion sorpresa
```

Devuelve 15 tags ES y 15 EN. **Recorta a los que sean verdad** y ajusta el contexto.

---

## Revisión final

- [ ] 10-15 tags.
- [ ] Todos describen el clip.
- [ ] Hay 3-5 amplios y 5-10 específicos.
- [ ] Hay emoción y contexto.
- [ ] Hay inglés si aplica.
- [ ] No hay tendencias irrelevantes.
- [ ] No hay errores de ortografía.
- [ ] No hay duplicados basura.
