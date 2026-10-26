# Proyecto de Francisco

Habla siempre en español, con palabras sencillas: el dueño no es programador.

## Sincronización Mac ↔ teléfono (muy importante)

El dueño trabaja a veces en su Mac y a veces desde el teléfono (sesiones en la nube).
GitHub es el único punto de encuentro, y la rama `main` es la versión compartida.

- **Al empezar**: trae lo último de `main` (`git pull origin main`) antes de tocar nada.
- **Al terminar cada tarea**: guarda (commit) y sube (push) a GitHub. No dejes nada
  solo en la máquina local. Si algo falla, avisa al dueño en una línea y explica qué pasó.
- **En sesiones en la nube** (rama `claude/...`): además de subir esa rama, sube el
  trabajo a `main` (`git push origin HEAD:main`) para que aparezca en el Mac. El dueño
  lo pidió explícitamente. Si `main` cambió mientras tanto, primero trae `main`, junta
  los cambios y vuelve a subir. Nunca uses `--force` sobre `main`.
- Usa mensajes de commit cortos y en español que digan qué cambió.
