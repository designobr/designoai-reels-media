---
name: threejs-advanced-developer
description: Desenvolve experiências 3D premium para web com Three.js (WebGL e WebGPU/TSL) e React Three Fiber. Use sempre que o pedido for site, landing page, hero, produto 3D, scroll 3D, animação cinematográfica, câmera com movimento profissional, iluminação e materiais realistas, shaders, pós-processamento, interface com profundidade ou qualquer experiência interativa tridimensional. Também use quando um site ou página se beneficiaria de elementos 3D, mesmo sem o usuário citar Three.js.
---

# Three.js Advanced Developer

Você constrói experiências 3D funcionais, não documentos. Cada entrega precisa rodar, ser verificada no navegador e ter acabamento visual de produto.

## 1. Quando aplicar automaticamente

Considere 3D sempre que o pedido envolver: landing page ou hero com profundidade, produto ou objeto em destaque, scroll que conta uma história, transições cinematográficas, fundos animados com partículas ou shaders, visualizações de dados em 3D, configuradores, portfólios de design ou motion. Se o 3D não agregar valor (ex.: formulário, blog, painel administrativo simples), não force. Diga em uma linha por que escolheu ou não escolheu 3D.

## 2. Escolha da stack

| Situação | Stack |
|---|---|
| Site estático, hero, peça isolada | `three` puro + Vite (template `vanilla-hero`) |
| Projeto React/Next.js ou muitos componentes 3D | `@react-three/fiber` + `@react-three/drei` (template `r3f-hero`) |
| Shaders com TSL, compute, máxima performance em hardware moderno | `three/webgpu` + `three/tsl` com `forceWebGL` opcional |

Regra: WebGL (`WebGLRenderer`) é o padrão, pois tem o maior alcance. Use WebGPU quando precisar de TSL, compute shaders ou node materials. Com `WebGPURenderer` passe `forceWebGL: true` se o alvo não suportar WebGPU.

Instalação (versões verificadas em `references/api-notes.md`):

```bash
# Vanilla
npm install three@0.187.0 && npm install -D vite@8.3.8
# React Three Fiber
npm install three@0.187.0 @react-three/fiber@9.8.2 @react-three/drei@10.7.9 react@19.3.1 react-dom@19.3.1
npm install -D vite@8.3.8
```

Antes de instalar em um projeto novo, rode `npm view three version` e prefira a versão mais recente estável que declare suporte ao R3F escolhido. Documente a versão escolhida.

## 3. Padrão de qualidade premium (obrigatório)

Renderer e cor:
- `renderer.toneMapping = THREE.ACESFilmicToneMapping` e `toneMappingExposure` entre 0.9 e 1.2.
- Saída sRGB pelo `OutputPass` quando houver pós-processamento.
- `setPixelRatio(Math.min(devicePixelRatio, 2))`. Em mobile, limite a 1.5.

Iluminação e materiais:
- Ambiente HDR com `PMREMGenerator`. Em ambiente com rede restrita, use `RoomEnvironment` (gerado em código, sem baixar `.hdr`). O template vanilla já faz isso; o R3F usa `templates/r3f-hero/src/offline-env.js`.
- Sombras: `PCFShadowMap` com `shadow.radius` e `mapSize` de 1024 a 2048. Não use `PCFSoftShadowMap` (removido no r187).
- Materiais PBR: `MeshStandardMaterial` ou `MeshPhysicalMaterial` (clearcoat, transmission, sheen, iridescence) para realismo. Evite `MeshBasicMaterial` para peças principais.
- Use uma luz principal, um preenchimento e um contraluz (rim). Três luzes bem posicionadas valem mais que dez.

Câmera e movimento:
- `OrbitControls` com `enableDamping = true` e `dampingFactor` entre 0.05 e 0.08. Limite `minDistance` e `maxDistance`.
- Transições de câmera com easing (ease-out cubic ou expo). Nunca salto linear.
- Scroll 3D: mapeie `scrollY / (height - innerHeight)` para progresso de 0 a 1 e interpole câmera e objetos com `lerp` a cada frame, não diretamente no evento de scroll.
- Respeite `prefers-reduced-motion`: desligue rotações automáticas e transições longas.

Tempo e loop:
- Use `THREE.Timer` (`timer.update(timestamp)`, `getDelta()`, `getElapsed()`). `THREE.Clock` está depreciado desde r183.
- Nunca aloque objetos (`new Vector3`, `new Matrix4`) dentro do loop de render. Reutilize.
- Pause o loop quando a seção sair da tela (IntersectionObserver) ou quando a aba estiver oculta (`visibilitychange`).

Performance:
- Objetos repetidos: `InstancedMesh` (um draw call).
- Modelos glTF: comprima com Draco ou meshopt, e texturas com KTX2 (`KTX2Loader`).
- Meta: menos de 100 draw calls, texturas no máximo 2048 px na peça principal, sem vazamento de GPU.
- Ao desmontar cena ou componente: `geometry.dispose()`, `material.dispose()`, `texture.dispose()`, `renderer.dispose()`. No React, faça isso no cleanup do `useEffect`.
- Redimensionamento: atualize `renderer.setSize`, `camera.aspect` e `updateProjectionMatrix` no `resize`.

Pós-processamento (ordem recomendada):
`RenderPass` → `UnrealBloomPass` (threshold alto, strength baixo, por exemplo 0.3 a 0.4) → `OutputPass`. Adicione `FXAA` ou `SMAA` se o antialias do renderer não bastar.

Interação:
- `Raycaster` para hover e clique, com `pointermove` e `pointerdown`. Em R3F use os handlers `onPointerOver`, `onClick` do próprio mesh.
- Feedback visual imediato: escala, cor ou emissão suave (com `lerp`).

## 4. Shaders e efeitos

- WebGL: `ShaderMaterial` (ou `RawShaderMaterial` com GLSL 3). Passe `uTime`, `uResolution`, `uMouse` como uniforms atualizados no loop.
- Modificar um material PBR existente: `material.onBeforeCompile` para injetar código sem perder iluminação.
- WebGPU: TSL (`three/tsl`). Veja exemplos `webgpu_tsl_*` em `references/examples-index.md`.
- Ruído, fresnel, dissolve, distorção por scroll e glitch são padrões comuns: consulte os exemplos antes de escrever do zero.

## 5. React Three Fiber

- `<Canvas shadows dpr={[1, 2]} camera={{...}}>` com `gl` e `shadows` configurados explicitamente (ver template).
- Atualize transformações dentro de `useFrame`, sem `setState`. Evita re-render a 60 fps.
- Ambientes: `<Environment preset="...">` baixa HDR da internet. Em rede restrita, gere o ambiente com `RoomEnvironment` (ver `templates/r3f-hero/src/offline-env.js`).
- Coloque `<Suspense>` em volta de carregamento de modelos e texturas.
- Drei oferece helpers prontos: `Float`, `ContactShadows`, `Html`, `Text`, `Center`, `Bounds`, `ScrollControls`, `PresentationControls`. Prefira-os a implementações manuais quando o resultado for equivalente.

## 6. Fluxo de trabalho

1. Defina a peça-chave, a câmera inicial, a paleta e o comportamento de scroll ou interação em uma frase cada.
2. Escolha o template (`templates/vanilla-hero` ou `templates/r3f-hero`), copie para o projeto e instale dependências.
3. Implemente a cena, depois ajuste iluminação e materiais olhando a imagem. Não confie só no código.
4. Rode `npm run build`. Corrija erros e avisos de depreciação.
5. Verifique no navegador com `scripts/verify-render.cjs` (ver seção 7) e leia as capturas.
6. Entregue com: caminho dos arquivos, dependências instaladas, resultado do build, resultado da verificação e limitações conhecidas.

## 7. Verificação no navegador

O ambiente tem Chromium pré-instalado. Não rode `npx playwright install`.

```bash
npm run build && npm run preview &
BASE_URL=http://127.0.0.1:4173 OUT_DIR=/caminho/para/capturas \
  NODE_PATH=$(npm root -g) node scripts/verify-render.cjs
```

O script abre cada página em 1280x720, aguarda o canvas, captura a tela e lista erros e avisos do console. Você deve ler a captura com a ferramenta de leitura de imagem e confirmar que a cena aparece. A métrica de brilho do script não é confiável (o canvas WebGL não tem `preserveDrawingBuffer`), use a captura visual.

Os templates têm uma única página em `/` (`index.html`). O script `verify-render.cjs` foi escrito para o projeto de teste, com duas páginas (`/` e `/r3f.html`). Ao usar um template, teste apenas a rota `/` ou ajuste a lista de páginas no script.

## 8. Avisos conhecidos (r187 e R3F 9.8.2)

- `THREE.Clock` depreciado: use `THREE.Timer`. O R3F 9.8.2 ainda usa `Clock` internamente e exibe o aviso. Ele não quebra a cena; registre como limitação, não tente remover dentro da biblioteca.
- `PCFSoftShadowMap` removido: use `PCFShadowMap`. Passe o tipo explicitamente na prop `shadows={{ type: THREE.PCFShadowMap }}` do Canvas.
- Carregamento de HDR remoto (drei `Environment preset`) pode falhar em rede restrita com `ERR_TUNNEL_CONNECTION_FAILED`. Use `RoomEnvironment`.
- WebGPU exige navegador compatível. Para testes headless, o WebGL via SwiftShader funciona; WebGPU pode não estar disponível.

## 9. Referências

- `references/examples-index.md`: exemplos oficiais por categoria, para consultar antes de implementar um efeito.
- `references/api-notes.md`: APIs atuais, imports, mudanças recentes e versões verificadas.
- `templates/vanilla-hero`: hero em Three.js puro com PBR, ambiente procedural, sombras, bloom, câmera com inércia e partículas instanciadas.
- `templates/r3f-hero`: mesma experiência em React Three Fiber, com ambiente offline e loop com `useFrame`.
- `scripts/verify-render.cjs`: verificação headless de renderização e console.

## 10. Limites honestos

- Não substitui design: se não houver direção de arte, proponha paleta, composição e movimento antes de codar.
- Medições de FPS em headless (SwiftShader) não representam hardware real. Reporte isso como limitação.
- Conteúdo de terceiros (modelos, HDRs, fontes) precisa de licença verificada antes de ir ao ar.
