# Exemplos oficiais do Three.js por categoria

Fonte: `examples/` do repositório `mrdoob/three.js` (branch `dev`, versão 0.187.0). Há 620 exemplos HTML: 244 `webgpu_*` e 297 `webgl_*`. Consulte o nome do arquivo para abrir o exemplo original, e copie a técnica, não o código inteiro.

Páginas da documentação: `https://threejs.org/docs/` (classes), `https://threejs.org/manual/` (guias), `https://threejs.org/docs/llms-full.txt` (referência completa para LLMs, inclui TSL).

## WebGPU e TSL (shaders, compute, efeitos avançados)
- `webgpu_tsl_earth`: terra com shaders procedurais
- `webgpu_tsl_galaxy`: galáxia com partículas
- `webgpu_tsl_compute_attractors_particles`: partículas com compute shader
- `webgpu_tsl_raging_sea`: mar procedural
- `webgpu_tsl_procedural_terrain`: terreno gerado em shader
- `webgpu_tsl_halftone`: efeito meio-tom
- `webgpu_tsl_angular_slicing`, `webgpu_tsl_noise_smoothing`, `webgpu_tsl_occlusion_dither`: efeitos de recorte e dithering
- `webgpu_tsl_graph`, `webgpu_tsl_editor`: como montar grafos de nós

## WebGL shaders
- `webgl_shader`, `webgl_shader_lava`, `webgl_shaders_ocean`, `webgl_shaders_sky`: shaders customizados completos

## Pós-processamento
- `webgl_postprocessing`: cadeia básica com `EffectComposer`
- `webgl_postprocessing_advanced`: pilha completa de efeitos
- `webgl_postprocessing_dof`, `webgl_postprocessing_dof2`: profundidade de campo
- `webgl_postprocessing_godrays`: raios de luz volumétricos
- `webgl_postprocessing_gtao`: oclusão ambiente
- `webgl_postprocessing_glitch`, `webgl_postprocessing_afterimage`: efeitos de estilo
- `webgl_postprocessing_3dlut`: correção de cor com LUT
- `webgl_postprocessing_fxaa`: antialias em pós
- `webgl_postprocessing_backgrounds`: fundos animados

Addons úteis (`examples/jsm/postprocessing/`): `UnrealBloomPass`, `SSAOPass`, `GTAOPass`, `SSRPass`, `OutlinePass`, `SMAAPass`, `BokehPass`, `FilmPass`, `HalftonePass`, `LUTPass`.

## Materiais e iluminação
- `webgl_materials_car`: pintura automotiva com clearcoat
- `webgl_materials_cubemap_refraction`, `webgl_materials_cubemap_dynamic`: reflexo e refração
- `webgl_materials_displacementmap`, `webgl_materials_bumpmap`: relevo
- `webgl_materials_blending_custom`: mistura customizada
- `webgl_lights_physical`, `webgl_lights_rectarealight`, `webgl_lights_sunlight`: iluminação física
- `webgl_lights_spotlight`, `webgl_lights_spotlights`, `webgl_lights_hemisphere`: luzes clássicas
- `webgpu_clearcoat`, `webgpu_caustics`, `webgpu_backdrop_water`: materiais avançados em WebGPU

## Sombras
- `webgl_shadowmap`: sombras básicas
- `webgl_shadowmap_pcss`: sombras suaves com PCSS
- `webgl_shadowmap_vsm`: variance shadow maps
- `webgl_shadowmap_csm`: cascaded shadow maps para cenas grandes
- `webgl_shadowmap_performance`: otimização de sombras
- `webgl_shadow_contact`: sombra de contato (chão de produto)

## Câmera e interação
- `webgl_camera`, `webgl_camera_array`, `webgl_camera_logarithmicdepthbuffer`: câmeras e profundidade
- `webgl_interactive_raycasting_points`, `webgl_interactive_cubes`: raycasting e hover
- `webgl_interactive_voxelpainter`: interação de pintura 3D
- `webgl_interactive_lines`: linhas interativas

## Animação e personagens
- `webgl_animation_skinning_blending`, `webgl_animation_skinning_additive_blending`: mistura de animações
- `webgl_animation_skinning_ik`: cinemática inversa
- `webgl_animation_skinning_morph`: morph targets
- `webgpu_animation_retargeting`: retargeting de animação

## glTF e modelos
- `webgl_loader_gltf`: carregamento básico
- `webgl_loader_gltf_compressed`: Draco, meshopt e KTX2
- `webgl_loader_gltf_variants`: variantes de produto (configurador)
- `webgl_loader_gltf_transmission`, `webgl_loader_gltf_iridescence`, `webgl_loader_gltf_sheen`, `webgl_loader_gltf_dispersion`: extensões de material
- `webgl_loader_gltf_progressive_lod`: níveis de detalhe progressivos

## Instancing e partículas
- `webgl_instancing_scatter`: espalhamento de objetos
- `webgl_instancing_performance`: milhares de objetos com poucos draw calls
- `webgl_instancing_dynamic`: instancing animado
- `webgl_instancing_raycast`: raycast em instâncias

## Ambiente e céu
- `webgl_shaders_sky`: céu procedural
- `webgpu_backdrop`, `webgpu_backdrop_area`: fundo com profundidade
