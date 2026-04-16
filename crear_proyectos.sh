#!/bin/bash

# Script para crear proyectos automáticamente

PROYECTOS=(
  "agentes-autonomos-monitoreo"
  "custom-commands-generator"
  "herramientas-productividad-dev"
  "portafolio-vibe-coding"
  "auditoria-codigo-parcheo"
  "agentes-seguridad-redteam"
  "blue-team-respuesta-incidentes"
  "gobernanza-cumplimiento-gcr"
  "guardrails-ia-seguridad"
)

for proyecto in "${PROYECTOS[@]}"; do
  if [ ! -d "$proyecto" ]; then
    mkdir -p "$proyecto"
    echo "✓ Creado: $proyecto"
  else
    echo "⚠ Ya existe: $proyecto"
  fi
done

echo ""
echo "=== Proyectos creados ==="
ls -la | grep -E "^d" | grep -v "^d.*\.$"
