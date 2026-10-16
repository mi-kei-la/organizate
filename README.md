# organizate

Un diagrama para ordenarte, hecho jueguito: te va haciendo preguntas, vos respondés, y al final te queda un resumen con lo que fuiste anotando.

**Jugalo acá:** https://mi-kei-la.github.io/organizate/

## Antes de arrancar

Esto no es una guía completa ni pretende serlo. Es una herramienta para darte una mano a organizarte vos y tus pendientes, nada más. Capaz te sirve, capaz no: usala como te quede cómoda.

No reemplaza ningún consejo profesional, y lo que hagas con ella corre por tu cuenta. No me hago responsable de ningún problema que te pueda traer.

Lo que escribís (objetivos, fechas, notas) queda guardado solo en tu navegador. No se manda a ningún lado.

## Cómo está hecho

- `scene.excalidraw.json`: el diagrama original, de Excalidraw.
- `build.py` y `template.html`: arman la página a partir del diagrama (las flechas son el grafo del juego).
- `fonts/`: Excalifont, con licencia SIL OFL 1.1.
- `index.html`: la página generada, que es lo que publica GitHub Pages.

Si cambiás el diagrama, exportá la escena de Excalidraw a `scene.excalidraw.json` y regenerá:

```
python3 -I build.py scene.excalidraw.json fonts template.html index.html --standalone
```
