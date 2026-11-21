import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

const container = document.getElementById('stage');
const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(container.clientWidth, container.clientHeight);
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFShadowMap;
container.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color('#07080b');
scene.fog = new THREE.Fog('#07080b', 9, 26);

// Ambiente HDR procedural: reflexos realistas sem carregar textura externa.
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;

const camera = new THREE.PerspectiveCamera(38, container.clientWidth / container.clientHeight, 0.1, 100);
camera.position.set(0, 1.4, 9);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.enablePan = false;
controls.minDistance = 5;
controls.maxDistance = 14;
controls.target.set(0, 0.2, 0);

// Luz principal com sombra suave + preenchimento frio.
const key = new THREE.DirectionalLight('#ffe7c4', 2.2);
key.position.set(4, 7, 5);
key.castShadow = true;
key.shadow.mapSize.set(2048, 2048);
key.shadow.radius = 6;
key.shadow.bias = -0.0004;
Object.assign(key.shadow.camera, { left: -6, right: 6, top: 6, bottom: -6, near: 1, far: 25 });
scene.add(key);

const rim = new THREE.SpotLight('#6fa8ff', 80, 30, Math.PI / 6, 0.6, 1.2);
rim.position.set(-5, 6, -4);
rim.target.position.set(0, 0, 0);
scene.add(rim, rim.target);

// Chão que recebe sombra e reflete suavemente.
const floor = new THREE.Mesh(
  new THREE.CircleGeometry(14, 96),
  new THREE.MeshStandardMaterial({ color: '#0d0f14', roughness: 0.55, metalness: 0.2 })
);
floor.rotation.x = -Math.PI / 2;
floor.position.y = -1.6;
floor.receiveShadow = true;
scene.add(floor);

// Peça hero: vidro físico com transmissão e clearcoat.
const hero = new THREE.Mesh(
  new THREE.TorusKnotGeometry(1.1, 0.38, 240, 36),
  new THREE.MeshPhysicalMaterial({
    color: '#c9d6ff', metalness: 0, roughness: 0.12,
    transmission: 0.92, thickness: 1.4, ior: 1.45,
    clearcoat: 1, clearcoatRoughness: 0.05, attenuationColor: '#7ba4ff', attenuationDistance: 2,
  })
);
hero.position.y = 0.4;
hero.castShadow = true;
scene.add(hero);

// Anel de partículas instanciadas (um draw call).
const COUNT = 420;
const dummy = new THREE.Object3D();
const dust = new THREE.InstancedMesh(
  new THREE.SphereGeometry(0.035, 8, 6),
  new THREE.MeshBasicMaterial({ color: '#f5d9a8' }),
  COUNT
);
for (let i = 0; i < COUNT; i++) {
  const a = (i / COUNT) * Math.PI * 2;
  const r = 2.6 + Math.sin(a * 5) * 0.35 + (Math.random() - 0.5) * 0.4;
  dummy.position.set(Math.cos(a) * r, Math.sin(a * 3) * 0.6 - 0.2, Math.sin(a) * r);
  dummy.scale.setScalar(0.6 + Math.random());
  dummy.updateMatrix();
  dust.setMatrixAt(i, dummy.matrix);
}
scene.add(dust);

// Pós-processamento: bloom leve só nos realces.
const composer = new EffectComposer(renderer);
composer.addPass(new RenderPass(scene, camera));
const bloom = new UnrealBloomPass(new THREE.Vector2(container.clientWidth, container.clientHeight), 0.35, 0.6, 0.85);
composer.addPass(bloom);
composer.addPass(new OutputPass());

// Entrada cinematográfica: a câmera desce e a peça ganha escala.
const intro = { t: 0 };
const timer = new THREE.Timer();

function resize() {
  const w = container.clientWidth, h = container.clientHeight;
  renderer.setSize(w, h);
  composer.setSize(w, h);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
}
window.addEventListener('resize', resize);

function frame(timestamp) {
  timer.update(timestamp);
  const dt = Math.min(timer.getDelta(), 0.05);
  const time = timer.getElapsed();
  intro.t = Math.min(intro.t + dt / 2.4, 1);
  const ease = 1 - Math.pow(1 - intro.t, 3);

  hero.scale.setScalar(0.6 + 0.4 * ease);
  if (!reduceMotion) {
    hero.rotation.x = time * 0.12;
    hero.rotation.y = time * 0.18;
    dust.rotation.y = time * 0.05;
    hero.position.y = 0.4 + Math.sin(time * 0.9) * 0.08;
  }
  camera.position.y = 1.4 - (1 - ease) * 1.2;

  controls.update();
  composer.render();
  requestAnimationFrame(frame);
}

window.__threeReady = false;
requestAnimationFrame(frame);
requestAnimationFrame(() => { window.__threeReady = true; });
