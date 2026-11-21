# Three.js: notas de API (versão verificada 0.187.0)

Verificado no repositório oficial `mrdoob/three.js` (branch `dev`), na versão declarada em `package.json`.

## Imports

```js
import * as THREE from 'three';                       // núcleo WebGL
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

import * as THREE from 'three/webgpu';                // WebGPURenderer e node materials
import { /* nós TSL */ } from 'three/tsl';           // Three Shading Language
```

Os caminhos vêm do `exports` do `package.json`: `./addons/*`, `./webgpu`, `./tsl`.

## Mudanças recentes a respeitar

| Item | Estado | Use no lugar |
|---|---|---|
| `THREE.Clock` | Depreciado desde r183 | `THREE.Timer` (`update(timestamp)`, `getDelta()`, `getElapsed()`) |
| `PCFSoftShadowMap` | Depreciado desde r186, removido na prática (aviso no console) | `PCFShadowMap` |
| `WebGPURenderer` sem WebGPU | Suporte a fallback | `new WebGPURenderer({ forceWebGL: true })` |

## Renderer

- `renderer.toneMapping = THREE.ACESFilmicToneMapping`
- `renderer.toneMappingExposure` entre 0.9 e 1.2
- `renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFShadowMap;`
- `renderer.setPixelRatio(Math.min(devicePixelRatio, 2))`
- Liberação: `renderer.dispose()` e `renderer.forceContextLoss()` apenas ao destruir a página inteira.

## Ambiente de iluminação

```js
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
pmrem.dispose();
```

Use HDR externo só quando houver licença e rede disponíveis (`RGBELoader` ou `HDRLoader` com `EquirectangularReflectionMapping`).

## Versões usadas nos templates

| Pacote | Versão |
|---|---|
| three | 0.187.0 |
| @react-three/fiber | 9.8.2 (requer React 19) |
| @react-three/drei | 10.7.9 |
| react, react-dom | 19.3.1 |
| vite | 8.3.8 |

Antes de atualizar, rode `npm view <pacote> version` e teste o build e a verificação de renderização.

## Avisos observados nos testes

- `THREE.Clock: This module has been deprecated`: vem do R3F 9.8.2 internamente. Documente como limitação.
- `PCFSoftShadowMap has been removed`: vinha da prop `shadows` do R3F por padrão. Resolvido passando `shadows={{ type: THREE.PCFShadowMap }}`.
- `GPU stall due to ReadPixels`: aviso do driver SwiftShader, causado pela medição de pixels no teste. Não é erro da cena.
- `Could not load potsdamer_platz_1k.hdr`: `<Environment preset>` tentou baixar HDR externo em rede restrita. Resolvido com `RoomEnvironment`.

## Bloom e pós-processamento

`UnrealBloomPass(resolution, strength, radius, threshold)`. Valores que funcionaram no template: `0.35, 0.6, 0.85`. Sempre finalize com `OutputPass` para a conversão de cor correta.

## Materiais

- `MeshPhysicalMaterial`: `clearcoat`, `clearcoatRoughness`, `transmission`, `thickness`, `ior`, `attenuationColor`, `attenuationDistance`, `sheen`, `iridescence`.
- Transmissão é cara: use poucas peças transmissivas por cena.
